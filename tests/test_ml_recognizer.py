import numpy as np
from ml_recognizer import ShapeRecognizer


class TestShapeRecognizer:
    def setup_method(self):
        self.recognizer = ShapeRecognizer()

    def test_recognize_rectangle(self, sample_contour_rectangle):
        shape = self.recognizer.recognize_shape(sample_contour_rectangle)
        assert shape == "Rectangle"

    def test_recognize_triangle(self, sample_contour_triangle):
        shape = self.recognizer.recognize_shape(sample_contour_triangle)
        assert shape == "Triangle"

    def test_recognize_circle(self, sample_contour_circle):
        shape = self.recognizer.recognize_shape(sample_contour_circle)
        assert shape == "Circle"

    def test_recognize_empty_contour(self):
        shape = self.recognizer.recognize_shape(None)
        assert shape == "Unknown"

    def test_recognize_small_contour(self):
        small = np.array([[0, 0], [1, 1]], dtype=np.int32).reshape((-1, 1, 2))
        shape = self.recognizer.recognize_shape(small)
        assert shape == "Unknown"

    def test_recognize_shape_from_points_insufficient(self):
        shape = self.recognizer.recognize_shape_from_points([(0, 0), (1, 1)])
        assert shape == "Unknown"

    def test_recognize_shape_from_points_sufficient(self):
        pts = [(50, 50), (200, 50), (200, 150), (50, 150), (50, 50)]
        shape = self.recognizer.recognize_shape_from_points(pts)
        assert shape == "Rectangle"

    def test_recognize_shape_from_points_empty(self):
        shape = self.recognizer.recognize_shape_from_points([])
        assert shape == "Unknown"


class TestDigitRecognizer:
    def test_recognize_digit_empty_image(self):
        from ml_recognizer import DigitRecognizer

        dr = DigitRecognizer()
        result = dr.recognize_digit(None)
        assert result is None

    def test_recognize_digit_blank_image(self):
        from ml_recognizer import DigitRecognizer

        dr = DigitRecognizer()
        blank = np.full((100, 100, 3), 0, dtype=np.uint8)
        result = dr.recognize_digit(blank)
        assert result is None
