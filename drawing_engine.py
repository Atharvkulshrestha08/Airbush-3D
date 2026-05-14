import cv2
import numpy as np


class DrawingEngine:
    def __init__(self):
        self.alpha = 0.3
        self.smoothed_x = None
        self.smoothed_y = None
        self.velocity_x = 0
        self.velocity_y = 0
        self.position_history = []
        self.history_size = 8

    def draw_line(
        self, x1: int, y1: int, x2: int, y2: int, color: tuple, canvas: np.ndarray
    ) -> np.ndarray:
        cv2.line(canvas, (x1, y1), (x2, y2), color, thickness=5)
        return canvas

    def draw_eraser(
        self, x1: int, y1: int, x2: int, y2: int, bg_color: tuple, canvas: np.ndarray
    ) -> np.ndarray:
        cv2.line(canvas, (x1, y1), (x2, y2), bg_color, thickness=30)
        return canvas

    def draw_highlighter(
        self, x1: int, y1: int, x2: int, y2: int, canvas: np.ndarray
    ) -> np.ndarray:
        cv2.line(canvas, (x1, y1), (x2, y2), (255, 255, 0), thickness=30)
        return canvas

    def draw_brush(
        self, x1: int, y1: int, x2: int, y2: int, color: tuple, canvas: np.ndarray
    ) -> np.ndarray:
        cv2.line(canvas, (x1, y1), (x2, y2), color, thickness=15)
        return canvas

    def smooth_position(self, x: int, y: int) -> tuple:
        self.position_history.append((x, y))
        if len(self.position_history) > self.history_size:
            self.position_history.pop(0)

        if len(self.position_history) < 3:
            if self.smoothed_x is None:
                self.smoothed_x, self.smoothed_y = x, y
            else:
                self.smoothed_x = int(
                    self.alpha * x + (1 - self.alpha) * self.smoothed_x
                )
                self.smoothed_y = int(
                    self.alpha * y + (1 - self.alpha) * self.smoothed_y
                )
            return (self.smoothed_x, self.smoothed_y)

        new_x = self.velocity_x + x
        new_y = self.velocity_y + y

        if self.smoothed_x is not None:
            prev_smoothed_x = self.smoothed_x
            prev_smoothed_y = self.smoothed_y

            self.smoothed_x = int(
                self.alpha * new_x + (1 - self.alpha) * self.smoothed_x
            )
            self.smoothed_y = int(
                self.alpha * new_y + (1 - self.alpha) * self.smoothed_y
            )

            self.velocity_x = int(
                0.7 * (self.smoothed_x - prev_smoothed_x) + 0.3 * self.velocity_x
            )
            self.velocity_y = int(
                0.7 * (self.smoothed_y - prev_smoothed_y) + 0.3 * self.velocity_y
            )
        else:
            self.smoothed_x = x
            self.smoothed_y = y
            self.velocity_x = 0
            self.velocity_y = 0

        return (self.smoothed_x, self.smoothed_y)

    def clear_position_buffer(self):
        self.smoothed_x = None
        self.smoothed_y = None
        self.velocity_x = 0
        self.velocity_y = 0
        self.position_history = []

    def clear_canvas(self, canvas: np.ndarray, bg_color: tuple) -> np.ndarray:
        canvas[:] = bg_color
        return canvas
