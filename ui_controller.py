import cv2
import numpy as np
import threading
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QComboBox,
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QColor

from camera_feed_handler import CameraFeedHandler
from drawing_engine import DrawingEngine
from hand_tracker import HandTracker
from drawing_mode import DrawingMode
from ml_recognizer import DigitRecognizer, ShapeRecognizer


class UIController(QMainWindow):
    mode_changed = pyqtSignal(DrawingMode)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AirBrush Studio")
        self.setGeometry(100, 100, 1280, 720)

        self.camera = CameraFeedHandler()
        self.engine = DrawingEngine()
        self.hand_tracker = HandTracker()

        self.digit_recognizer = DigitRecognizer()
        self.shape_recognizer = ShapeRecognizer()

        self.drawing_mode = DrawingMode.MODE_NONE
        self.pen_color = (0, 0, 255)
        self.highlighter_color = (255, 255, 0)
        self.brush_color = (0, 165, 255)
        self.canvas_color = (255, 255, 255)
        self.is_drawing = False
        self.last_point = None
        self.prev_smooth_point = None
        self.prev_tip_pos = None
        self.gesture_stable_count = 0
        self.required_stable_frames = 2
        self.hand_was_lost = True
        self.tip_velocity_x = 0
        self.tip_velocity_y = 0
        self.last_detected_mode = DrawingMode.MODE_NONE

        self.sketch_canvas = None
        self.frame_shape = None

        self.shape_mode = "None"
        self.shape_drawing_active = False
        self.current_shape_points = None

        self.current_stroke_points = []
        self.hold_frames = 0

        self.trail_points = []

        self._init_ui()
        self._init_camera()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.setStyleSheet("""
            QWidget {
                background-color: #0e0e0e;
                color: #ffffff;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
            QLabel { color: #adaaaa; }
            QLabel#titleText {
                color: #81ecff;
                font-size: 24px;
                font-weight: 900;
                letter-spacing: 1px;
            }
            QLabel#panelHeader {
                color: #c500e6;
                font-size: 11px;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            QLabel#controlLabel {
                color: #565555;
                font-size: 10px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00e3fd, stop:1 #81ecff);
                color: #001835;
                font-size: 14px;
                font-weight: 800;
                border-radius: 12px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #81ecff, stop:1 #00e3fd);
            }
            QPushButton#toolBtn {
                background-color: #1a1a1a;
                color: #adaaaa;
                border: 1px solid #262626;
                border-radius: 12px;
            }
            QPushButton#toolBtn:hover {
                background-color: #262626;
                color: #ffffff;
            }
            QComboBox {
                background-color: #161616;
                border: 1px solid #262626;
                border-radius: 10px;
                padding: 10px 14px;
                color: #ffffff;
                font-weight: 500;
            }
            QComboBox::drop-down { border: none; }
            QLabel#modeActive {
                background-color: #161616;
                border: 1px solid #262626;
                border-radius: 10px;
                padding: 10px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#mlResult {
                background-color: #131313;
                border-left: 4px solid #81ecff;
                border-radius: 8px;
                padding: 16px;
                color: #ffffff;
                font-size: 16px;
                font-weight: 800;
            }
        """)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)

        left_panel = QWidget()
        left_panel.setFixedWidth(120)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        title_lbl = QLabel("AirBrush")
        title_lbl.setObjectName("titleText")
        title_lbl.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title_lbl)

        left_layout.addSpacing(20)

        left_layout.addWidget(QLabel("Active Mode:"), alignment=Qt.AlignCenter)
        self.mode_display = QLabel("None")
        self.mode_display.setObjectName("modeActive")
        self.mode_display.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.mode_display)

        self.gesture_label = QLabel("Scanning...")
        self.gesture_label.setAlignment(Qt.AlignCenter)
        self.gesture_label.setStyleSheet("color: #81ecff; font-size: 11px;")
        left_layout.addWidget(self.gesture_label)

        left_layout.addStretch()

        clear_btn = QPushButton("Clear\nCanvas")
        clear_btn.setObjectName("toolBtn")
        clear_btn.setMinimumHeight(60)
        clear_btn.clicked.connect(self.clear_canvas)
        left_layout.addWidget(clear_btn)

        canvas_container = QWidget()
        canvas_container.setStyleSheet(
            "background-color: #1a1a1a; border: 2px solid #262626; border-radius: 16px;"
        )
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(5, 5, 5, 5)

        self.canvas_label = QLabel()
        self.canvas_label.setMinimumSize(800, 600)
        self.canvas_label.setAlignment(Qt.AlignCenter)
        canvas_layout.addWidget(self.canvas_label)

        right_panel = QWidget()
        right_panel.setFixedWidth(280)
        right_panel.setStyleSheet(
            "background-color: #131313; border-radius: 16px; border: 1px solid #1a1a1a;"
        )
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 24, 20, 24)
        right_layout.setSpacing(16)

        ml_header = QLabel("ML Controls")
        ml_header.setObjectName("panelHeader")
        right_layout.addWidget(ml_header)

        right_layout.addSpacing(8)

        shape_lbl = QLabel("Shape Mode Selector")
        shape_lbl.setObjectName("controlLabel")
        right_layout.addWidget(shape_lbl)

        self.shape_selector = QComboBox()
        self.shape_selector.addItems(["None", "Rectangle", "Circle", "Triangle"])
        right_layout.addWidget(self.shape_selector)

        right_layout.addSpacing(10)

        ml_mode_lbl = QLabel("ML Recognition Mode")
        ml_mode_lbl.setObjectName("controlLabel")
        right_layout.addWidget(ml_mode_lbl)

        self.ml_selector = QComboBox()
        self.ml_selector.addItems(["None", "Digit Recognition", "Shape Recognition"])
        right_layout.addWidget(self.ml_selector)

        right_layout.addStretch()

        self.ml_result_label = QLabel("LIVE READOUT\nWaiting for Data...")
        self.ml_result_label.setObjectName("mlResult")
        right_layout.addWidget(self.ml_result_label)

        right_layout.addSpacing(8)

        coord_lbl = QLabel("Finger XY Position")
        coord_lbl.setObjectName("controlLabel")
        right_layout.addWidget(coord_lbl)

        self.finger_graph_label = QLabel()
        self.finger_graph_label.setFixedSize(240, 200)
        self.finger_graph_label.setAlignment(Qt.AlignCenter)
        self.finger_graph_label.setStyleSheet(
            "background-color: #0a0a0a; border: 1px solid #262626; border-radius: 8px;"
        )
        right_layout.addWidget(self.finger_graph_label, alignment=Qt.AlignCenter)

        right_layout.addSpacing(10)

        export_btn = QPushButton("Export Image (PNG)")
        export_btn.setMinimumHeight(48)
        export_btn.clicked.connect(self.export_image)
        right_layout.addWidget(export_btn)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(canvas_container, 1)
        main_layout.addWidget(right_panel)

    def _init_camera(self):
        self.camera.start()
        frame = self.camera.get_frame()
        self.frame_shape = frame.shape
        self.sketch_canvas = np.full(
            (frame.shape[0], frame.shape[1], 3), self.canvas_color, dtype=np.uint8
        )

    def clear_canvas(self):
        if self.sketch_canvas is not None:
            self.sketch_canvas = self.engine.clear_canvas(
                self.sketch_canvas, self.canvas_color
            )

    def export_image(self):
        if self.sketch_canvas is not None:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Image", "drawing.png", "PNG Files (*.png);;All Files (*)"
            )
            if file_path:
                cv2.imwrite(file_path, self.sketch_canvas)

    def update_frame(self):
        frame = self.camera.get_frame()

        results = self.hand_tracker.process_frame(frame)

        gesture = self.hand_tracker.detect_gesture(results)
        self.gesture_label.setText(f"Gesture: {gesture}")

        if gesture == "pen":
            new_mode = DrawingMode.MODE_PEN
            mode_text = "Pen"
            mode_style = "color: #ff716c; border-color: #ff716c; background-color: rgba(255, 113, 108, 0.1);"
        elif gesture == "eraser":
            new_mode = DrawingMode.MODE_ERASER
            mode_text = "Eraser"
            mode_style = "color: #adaaaa; border-color: #adaaaa;"
        elif gesture == "highlighter":
            new_mode = DrawingMode.MODE_HIGHLIGHTER
            mode_text = "Highlighter"
            mode_style = "color: #f7a8ff; border-color: #f7a8ff; background-color: rgba(247, 168, 255, 0.1);"
        elif gesture == "brush":
            new_mode = DrawingMode.MODE_BRUSH
            mode_text = "Brush"
            mode_style = "color: #00d4ec; border-color: #00d4ec; background-color: rgba(0, 212, 236, 0.1);"
        else:
            new_mode = DrawingMode.MODE_NONE
            mode_text = "None"
            mode_style = "color: #adaaaa; border-color: #262626;"

        if new_mode == self.last_detected_mode:
            self.gesture_stable_count += 1
        else:
            self.gesture_stable_count = 0
            self.last_detected_mode = new_mode

        if (
            self.gesture_stable_count >= self.required_stable_frames
            and new_mode != self.drawing_mode
        ):
            self.drawing_mode = new_mode
            self.mode_display.setText(mode_text)
            self.mode_display.setStyleSheet(mode_style)

        tip_pos = self.hand_tracker.get_index_finger_tip(
            results, frame.shape, self.prev_tip_pos, self.hand_was_lost
        )

        if tip_pos:
            if self.hand_was_lost and self.prev_tip_pos:
                dist = (
                    (tip_pos[0] - self.prev_tip_pos[0]) ** 2
                    + (tip_pos[1] - self.prev_tip_pos[1]) ** 2
                ) ** 0.5
                if dist > 100:
                    tip_pos = self.prev_tip_pos
                    self.hand_was_lost = False
                else:
                    self.tip_velocity_x = 0
                    self.tip_velocity_y = 0
                    self.hand_was_lost = False
            else:
                if self.prev_tip_pos:
                    raw_vel_x = tip_pos[0] - self.prev_tip_pos[0]
                    raw_vel_y = tip_pos[1] - self.prev_tip_pos[1]
                    self.tip_velocity_x = int(
                        0.6 * raw_vel_x + 0.4 * self.tip_velocity_x
                    )
                    self.tip_velocity_y = int(
                        0.6 * raw_vel_y + 0.4 * self.tip_velocity_y
                    )

            self.prev_tip_pos = tip_pos
        else:
            self.hand_was_lost = True

        if tip_pos and self.drawing_mode != DrawingMode.MODE_NONE:
            smooth_pos = self.engine.smooth_position(tip_pos[0], tip_pos[1])

            if self.prev_smooth_point is not None:
                dist = (
                    (self.prev_smooth_point[0] - smooth_pos[0]) ** 2
                    + (self.prev_smooth_point[1] - smooth_pos[1]) ** 2
                ) ** 0.5

                if dist > 2:
                    if self.drawing_mode == DrawingMode.MODE_PEN:
                        self.sketch_canvas = self.engine.draw_line(
                            self.prev_smooth_point[0],
                            self.prev_smooth_point[1],
                            smooth_pos[0],
                            smooth_pos[1],
                            self.pen_color,
                            self.sketch_canvas,
                        )

                        if dist < 5:
                            self.hold_frames += 1
                        else:
                            self.hold_frames = 0

                        self.current_stroke_points.append(smooth_pos)

                        if (
                            self.hold_frames > 20
                            and len(self.current_stroke_points) > 20
                        ):
                            shape = self.shape_recognizer.recognize_shape_from_points(
                                self.current_stroke_points
                            )
                            if shape in ["Circle", "Rectangle", "Square", "Triangle"]:
                                for i in range(1, len(self.current_stroke_points)):
                                    cv2.line(
                                        self.sketch_canvas,
                                        self.current_stroke_points[i - 1],
                                        self.current_stroke_points[i],
                                        self.canvas_color,
                                        10,
                                    )

                                draw_shape = "Rectangle" if shape == "Square" else shape
                                self._finalize_shape(
                                    self.current_stroke_points, draw_shape
                                )

                            self.current_stroke_points = []
                            self.hold_frames = 0

                    elif self.drawing_mode == DrawingMode.MODE_ERASER:
                        self.current_stroke_points = []
                        self.hold_frames = 0
                        self.sketch_canvas = self.engine.draw_eraser(
                            self.prev_smooth_point[0],
                            self.prev_smooth_point[1],
                            smooth_pos[0],
                            smooth_pos[1],
                            self.canvas_color,
                            self.sketch_canvas,
                        )
                    elif self.drawing_mode == DrawingMode.MODE_HIGHLIGHTER:
                        self.current_stroke_points = []
                        self.hold_frames = 0
                        self.sketch_canvas = self.engine.draw_highlighter(
                            self.prev_smooth_point[0],
                            self.prev_smooth_point[1],
                            smooth_pos[0],
                            smooth_pos[1],
                            self.sketch_canvas,
                        )
                    elif self.drawing_mode == DrawingMode.MODE_BRUSH:
                        self.current_stroke_points = []
                        self.hold_frames = 0
                        self.sketch_canvas = self.engine.draw_brush(
                            self.prev_smooth_point[0],
                            self.prev_smooth_point[1],
                            smooth_pos[0],
                            smooth_pos[1],
                            self.brush_color,
                            self.sketch_canvas,
                        )
            self.prev_smooth_point = smooth_pos
        else:
            self.prev_smooth_point = None
            self.current_stroke_points = []
            self.hold_frames = 0
            self.engine.clear_position_buffer()

        frame = self.hand_tracker.draw_landmarks(frame, results)

        self.shape_mode = self.shape_selector.currentText()

        all_points = self.hand_tracker.get_all_four_points(results, frame.shape)
        is_finalize_gesture = self.hand_tracker.detect_middle_finger_raise(results)

        if self.shape_mode != "None":
            if all_points and not is_finalize_gesture:
                if not self.shape_drawing_active:
                    self.shape_drawing_active = True

                self.current_shape_points = all_points
                self._draw_shape_preview(all_points, self.shape_mode)

            elif self.shape_drawing_active and is_finalize_gesture:
                if self.current_shape_points:
                    self._finalize_shape(self.current_shape_points, self.shape_mode)
                self.shape_drawing_active = False
                self.current_shape_points = None
        else:
            self.shape_drawing_active = False
            self.current_shape_points = None

        self._draw_coordinate_graph(self.prev_tip_pos, frame.shape)
        self._update_display(frame)

    def _draw_shape_preview(self, points, shape_mode):
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]

        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)

        preview_color = (100, 255, 100)

        if shape_mode == "Rectangle":
            cv2.rectangle(
                self.sketch_canvas, (min_x, min_y), (max_x, max_y), preview_color, 2
            )
        elif shape_mode == "Circle":
            center = ((min_x + max_x) // 2, (min_y + max_y) // 2)
            radius = min((max_x - min_x) // 2, (max_y - min_y) // 2)
            cv2.circle(self.sketch_canvas, center, radius, preview_color, 2)
        elif shape_mode == "Triangle":
            pts = np.array(
                [[min_x, min_y], [max_x, min_y], [(min_x + max_x) // 2, max_y]],
                np.int32,
            )
            cv2.polylines(self.sketch_canvas, [pts], True, preview_color, 2)

    def _finalize_shape(self, points, shape_mode):
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]

        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)

        final_color = (0, 255, 0)

        if shape_mode == "Rectangle":
            cv2.rectangle(
                self.sketch_canvas, (min_x, min_y), (max_x, max_y), final_color, 3
            )
        elif shape_mode == "Circle":
            center = ((min_x + max_x) // 2, (min_y + max_y) // 2)
            radius = min((max_x - min_x) // 2, (max_y - min_y) // 2)
            cv2.circle(self.sketch_canvas, center, radius, final_color, 3)
        elif shape_mode == "Triangle":
            pts = np.array(
                [[min_x, min_y], [max_x, min_y], [(min_x + max_x) // 2, max_y]],
                np.int32,
            )
            cv2.polylines(self.sketch_canvas, [pts], True, final_color, 3)

    def _draw_coordinate_graph(self, tip_pos, frame_shape):
        W, H = 240, 200
        pad = 30
        plot_w = W - 2 * pad
        plot_h = H - 2 * pad
        graph = np.full((H, W, 3), 10, dtype=np.uint8)

        if tip_pos:
            self.trail_points.append(tip_pos)
            if len(self.trail_points) > 80:
                self.trail_points.pop(0)

        fw, fh = frame_shape[1], frame_shape[0]

        for x in range(pad, W - pad + 1, plot_w // 4):
            cv2.line(graph, (x, pad), (x, H - pad), (30, 30, 30), 1)
        for y in range(pad, H - pad + 1, plot_h // 4):
            cv2.line(graph, (pad, y), (W - pad, y), (30, 30, 30), 1)

        cv2.rectangle(graph, (pad, pad), (W - pad, H - pad), (50, 50, 50), 1)

        cv2.putText(
            graph,
            "0",
            (pad - 12, H - pad + 14),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (80, 80, 80),
            1,
        )
        cv2.putText(
            graph,
            str(fw),
            (W - pad - 20, H - pad + 14),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (80, 80, 80),
            1,
        )
        cv2.putText(
            graph,
            str(fh),
            (4, pad + 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (80, 80, 80),
            1,
        )
        cv2.putText(
            graph,
            "X",
            (W - pad + 2, H - pad + 14),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (60, 60, 60),
            1,
        )
        cv2.putText(
            graph,
            "Y",
            (4, pad - 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (60, 60, 60),
            1,
        )

        for pt in self.trail_points[:-1]:
            gx = pad + int(pt[0] / fw * plot_w)
            gy = pad + int(pt[1] / fh * plot_h)
            cv2.circle(graph, (gx, gy), 2, (40, 80, 120), -1)

        if self.trail_points:
            pt = self.trail_points[-1]
            gx = pad + int(pt[0] / fw * plot_w)
            gy = pad + int(pt[1] / fh * plot_h)
            cv2.circle(graph, (gx, gy), 6, (0, 200, 255), -1)
            cv2.circle(graph, (gx, gy), 8, (0, 200, 255), 1)

            coord_text = f"({pt[0]}, {pt[1]})"
            cv2.putText(
                graph,
                coord_text,
                (pad, pad + 14),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 200, 255),
                1,
            )

        rgb = cv2.cvtColor(graph, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.finger_graph_label.setPixmap(QPixmap.fromImage(qt_img))

    def _update_display(self, frame):
        combined = cv2.addWeighted(frame, 0.5, self.sketch_canvas, 0.5, 0)

        ml_mode = self.ml_selector.currentText()
        if ml_mode == "Digit Recognition":
            digit_result = self.digit_recognizer.recognize_digit(self.sketch_canvas)
            if digit_result:
                self.ml_result_label.setText(
                    f"LIVE READOUT\nDigit {digit_result} Detected"
                )
        elif ml_mode == "Shape Recognition":
            gray_canvas = cv2.cvtColor(self.sketch_canvas, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray_canvas, 200, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(
                binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest_contour) > 500:
                    shape = self.shape_recognizer.recognize_shape(largest_contour)
                    self.ml_result_label.setText(f"LIVE READOUT\n{shape} Detected")
        else:
            self.ml_result_label.setText("LIVE READOUT\nWaiting for Data...")

        rgb_frame = cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qt_image)
        self.canvas_label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.camera.stop()
        super().closeEvent(event)


def main():
    import sys

    app = QApplication(sys.argv)
    window = UIController()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
