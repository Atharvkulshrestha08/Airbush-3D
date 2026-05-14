import numpy as np
from main import AirBrushStudio
from drawing_mode import DrawingMode


class TestAirBrushStudio:
    def setup_method(self):
        self.app = AirBrushStudio()

    def test_initial_mode(self):
        assert self.app.drawing_mode == DrawingMode.MODE_PEN

    def test_set_drawing_mode(self):
        self.app.set_drawing_mode(DrawingMode.MODE_ERASER)
        assert self.app.get_drawing_mode() == DrawingMode.MODE_ERASER

    def test_set_pen_color(self):
        self.app.set_pen_color((0, 255, 0))
        assert self.app.pen_color == (0, 255, 0)

    def test_process_input_not_pressed(self):
        canvas = np.full((100, 100, 3), 255, dtype=np.uint8)
        result = self.app.process_input(10, 10, False, canvas)
        assert result is canvas
        assert self.app.is_drawing is False
        assert self.app.last_point is None

    def test_process_input_first_point(self):
        canvas = np.full((100, 100, 3), 255, dtype=np.uint8)
        result = self.app.process_input(10, 10, True, canvas)
        assert result is canvas
        assert self.app.last_point == (10, 10)

    def test_process_input_pen_draw(self):
        canvas = np.full((100, 100, 3), 255, dtype=np.uint8)
        self.app.process_input(10, 10, True, canvas)
        self.app.drawing_mode = DrawingMode.MODE_PEN
        result = self.app.process_input(50, 50, True, canvas)
        assert result is canvas
        assert self.app.last_point == (50, 50)

    def test_process_input_eraser_draw(self):
        canvas = np.full((100, 100, 3), 255, dtype=np.uint8)
        self.app.process_input(10, 10, True, canvas)
        self.app.drawing_mode = DrawingMode.MODE_ERASER
        result = self.app.process_input(50, 50, True, canvas)
        assert result is canvas
        assert self.app.last_point == (50, 50)

    def test_clear_canvas(self):
        result = self.app.clear_canvas((100, 100, 3))
        assert np.all(result == 255)
        assert result.shape == (100, 100, 3)
