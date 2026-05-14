from drawing_mode import DrawingMode


class TestDrawingMode:
    def test_mode_values(self):
        assert DrawingMode.MODE_NONE.value == "none"
        assert DrawingMode.MODE_PEN.value == "pen"
        assert DrawingMode.MODE_ERASER.value == "eraser"
        assert DrawingMode.MODE_HIGHLIGHTER.value == "highlighter"
        assert DrawingMode.MODE_BRUSH.value == "brush"

    def test_mode_distinct(self):
        modes = [
            DrawingMode.MODE_NONE,
            DrawingMode.MODE_PEN,
            DrawingMode.MODE_ERASER,
            DrawingMode.MODE_HIGHLIGHTER,
            DrawingMode.MODE_BRUSH,
        ]
        assert len(set(modes)) == 5

    def test_mode_membership(self):
        assert DrawingMode("none") == DrawingMode.MODE_NONE
        assert DrawingMode("pen") == DrawingMode.MODE_PEN

    def test_mode_iteration(self):
        all_modes = list(DrawingMode)
        assert len(all_modes) == 5
