import numpy as np
from hand_tracker import HandTracker


class MockLandmark:
    def __init__(self, x=0.5, y=0.5, z=0.0):
        self.x = x
        self.y = y
        self.z = z


def _build_landmarks(index_ext, middle_ext, ring_ext, pinky_ext, thumb_ext=True):
    lms = [MockLandmark(0.5, 0.5) for _ in range(21)]

    mcp_y, pip_y, tip_y = 0.6, 0.5, 0.3

    def set_finger(mcp, pip, dip, tip, extended):
        lms[mcp] = MockLandmark(0.5, mcp_y)
        y = pip_y if extended else mcp_y + 0.02
        lms[pip] = MockLandmark(0.5, y)
        lms[dip] = MockLandmark(0.5, (y + tip_y) / 2)
        lms[tip] = MockLandmark(0.5, tip_y if extended else y + 0.05)

    set_finger(5, 6, 7, 8, index_ext)
    set_finger(9, 10, 11, 12, middle_ext)
    set_finger(13, 14, 15, 16, ring_ext)
    set_finger(17, 18, 19, 20, pinky_ext)

    if thumb_ext:
        lms[3] = MockLandmark(0.45, 0.55)
        lms[4] = MockLandmark(0.40, 0.50)
    else:
        lms[3] = MockLandmark(0.48, 0.55)
        lms[4] = MockLandmark(0.49, 0.52)

    return lms


class TestHandTracker:
    def setup_method(self):
        self.tracker = HandTracker()
        self.tracker.gesture_history = []

    def test_process_frame_no_results(self):
        result = self.tracker.get_index_finger_tip(
            None, (480, 640, 3), prev_pos=(100, 100), hand_was_lost=False
        )
        assert result is None

    def test_get_index_finger_tip_no_landmarks(self):
        class MockResults:
            hand_landmarks = []

        result = self.tracker.get_index_finger_tip(MockResults(), (480, 640, 3))
        assert result is None

    def test_detect_gesture_no_results(self):
        result = self.tracker.detect_gesture(None)
        assert result is not None

    def test_detect_gesture_pen(self):
        lms = _build_landmarks(True, False, False, False)

        class MockResults:
            hand_landmarks = [lms]

        for _ in range(10):
            gesture = self.tracker.detect_gesture(MockResults())
        assert gesture == "pen"

    def test_detect_gesture_eraser(self):
        lms = _build_landmarks(True, True, True, True)

        class MockResults:
            hand_landmarks = [lms]

        for _ in range(10):
            gesture = self.tracker.detect_gesture(MockResults())
        assert gesture == "eraser"

    def test_detect_gesture_highlighter(self):
        lms = _build_landmarks(True, True, False, False)

        class MockResults:
            hand_landmarks = [lms]

        for _ in range(10):
            gesture = self.tracker.detect_gesture(MockResults())
        assert gesture == "highlighter"

    def test_detect_gesture_brush(self):
        lms = _build_landmarks(True, True, True, False)

        class MockResults:
            hand_landmarks = [lms]

        for _ in range(10):
            gesture = self.tracker.detect_gesture(MockResults())
        assert gesture == "brush"

    def test_detect_fist_no_hands(self):
        assert not self.tracker.detect_fist(None)

    def test_detect_middle_finger_raise_no_hands(self):
        assert not self.tracker.detect_middle_finger_raise(None)

    def test_get_two_hand_positions_insufficient_hands(self):
        result = self.tracker.get_two_hand_positions(None, (480, 640, 3))
        assert result == (None, None)

    def test_get_four_point_gesture_insufficient_hands(self):
        result = self.tracker.get_four_point_gesture(None, (480, 640, 3))
        assert result is None

    def test_get_all_four_points_insufficient_hands(self):
        result = self.tracker.get_all_four_points(None, (480, 640, 3))
        assert result is None

    def test_draw_landmarks_no_results(self):
        frame = np.full((100, 100, 3), 0, dtype=np.uint8)
        result = self.tracker.draw_landmarks(frame, None)
        assert result is frame
