import numpy as np
from drawing_engine import DrawingEngine


class TestDrawingEngine:
    def setup_method(self):
        self.engine = DrawingEngine()
        self.canvas = np.full((480, 640, 3), 255, dtype=np.uint8)

    def test_draw_line(self):
        result = self.engine.draw_line(10, 10, 100, 100, (0, 0, 255), self.canvas)
        assert result is self.canvas
        assert result[55, 55].tolist() == [0, 0, 255]
        assert result[0, 0].tolist() == [255, 255, 255]

    def test_draw_eraser(self):
        self.canvas[50, 50] = [0, 0, 255]
        result = self.engine.draw_eraser(10, 10, 100, 100, (255, 255, 255), self.canvas)
        assert result is self.canvas

    def test_draw_highlighter(self):
        result = self.engine.draw_highlighter(10, 10, 100, 100, self.canvas)
        assert result is self.canvas

    def test_draw_brush(self):
        result = self.engine.draw_brush(10, 10, 100, 100, (0, 165, 255), self.canvas)
        assert result is self.canvas

    def test_smooth_position_first_call(self):
        pos = self.engine.smooth_position(100, 200)
        assert pos == (100, 200)

    def test_smooth_position_second_call(self):
        self.engine.smooth_position(100, 200)
        pos = self.engine.smooth_position(110, 210)
        assert pos[0] != 110
        assert pos[1] != 210

    def test_smooth_position_within_history(self):
        for _ in range(10):
            self.engine.smooth_position(100, 200)
        pos = self.engine.smooth_position(105, 205)
        assert isinstance(pos[0], int)
        assert isinstance(pos[1], int)

    def test_clear_position_buffer(self):
        self.engine.smooth_position(100, 200)
        self.engine.smooth_position(110, 210)
        self.engine.clear_position_buffer()
        assert self.engine.smoothed_x is None
        assert self.engine.smoothed_y is None
        assert self.engine.position_history == []

    def test_clear_canvas(self):
        self.canvas[100, 100] = [0, 0, 255]
        result = self.engine.clear_canvas(self.canvas, (255, 255, 255))
        assert np.all(result == 255)
        assert result is self.canvas

    def test_clear_canvas_different_color(self):
        result = self.engine.clear_canvas(self.canvas, (0, 0, 0))
        assert np.all(result == 0)
