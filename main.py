import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QButtonGroup,
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor

from camera_feed_handler import CameraFeedHandler
from drawing_engine import DrawingEngine
from ui_controller import UIController
from drawing_mode import DrawingMode


class AirBrushStudio:
    def __init__(self):
        self.drawing_mode = DrawingMode.MODE_PEN
        self.pen_color = (0, 0, 255)
        self.eraser_color = (255, 255, 255)
        self.canvas_color = (255, 255, 255)
        self.is_drawing = False
        self.last_point = None

    def set_drawing_mode(self, mode: DrawingMode):
        self.drawing_mode = mode

    def get_drawing_mode(self) -> DrawingMode:
        return self.drawing_mode

    def set_pen_color(self, color: tuple):
        self.pen_color = color

    def process_input(
        self, x: int, y: int, is_pressed: bool, sketch_canvas: np.ndarray
    ):
        if not is_pressed:
            self.is_drawing = False
            self.last_point = None
            return sketch_canvas

        if self.last_point is None:
            self.last_point = (x, y)
            return sketch_canvas

        engine = DrawingEngine()

        if self.drawing_mode == DrawingMode.MODE_PEN:
            sketch_canvas = engine.draw_line(
                self.last_point[0],
                self.last_point[1],
                x,
                y,
                self.pen_color,
                sketch_canvas,
            )
        elif self.drawing_mode == DrawingMode.MODE_ERASER:
            sketch_canvas = engine.draw_eraser(
                self.last_point[0],
                self.last_point[1],
                x,
                y,
                self.canvas_color,
                sketch_canvas,
            )

        self.last_point = (x, y)
        return sketch_canvas

    def clear_canvas(self, canvas_shape: tuple):
        return np.full(canvas_shape, self.canvas_color, dtype=np.uint8)
