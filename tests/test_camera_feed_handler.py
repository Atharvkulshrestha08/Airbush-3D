import numpy as np
from unittest.mock import patch, MagicMock


class TestCameraFeedHandler:
    def test_initial_state(self):
        from camera_feed_handler import CameraFeedHandler

        cam = CameraFeedHandler()
        assert cam.camera_index == 0
        assert cam.cap is None
        assert cam.current_frame is None

    @patch("cv2.VideoCapture")
    def test_start_camera(self, mock_vc):
        from camera_feed_handler import CameraFeedHandler

        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = True
        mock_vc.return_value = mock_instance

        cam = CameraFeedHandler()
        cam.start()
        assert cam.cap is not None
        mock_vc.assert_called_once_with(0)

    @patch("cv2.VideoCapture")
    def test_start_camera_failure(self, mock_vc):
        from camera_feed_handler import CameraFeedHandler

        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = False
        mock_vc.return_value = mock_instance

        cam = CameraFeedHandler()
        import pytest

        with pytest.raises(RuntimeError, match="Cannot open camera"):
            cam.start()

    @patch("cv2.VideoCapture")
    def test_get_frame(self, mock_vc):
        from camera_feed_handler import CameraFeedHandler

        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (
            True,
            np.full((100, 100, 3), 0, dtype=np.uint8),
        )
        mock_vc.return_value = mock_instance

        cam = CameraFeedHandler()
        frame = cam.get_frame()
        assert frame is not None
        assert frame.shape == (100, 100, 3)

    @patch("cv2.VideoCapture")
    def test_get_frame_failure(self, mock_vc):
        from camera_feed_handler import CameraFeedHandler

        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (False, None)
        mock_vc.return_value = mock_instance

        cam = CameraFeedHandler()
        import pytest

        with pytest.raises(RuntimeError, match="Failed to capture frame"):
            cam.get_frame()

    @patch("cv2.VideoCapture")
    def test_get_current_frame(self, mock_vc):
        from camera_feed_handler import CameraFeedHandler

        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (
            True,
            np.full((100, 100, 3), 0, dtype=np.uint8),
        )
        mock_vc.return_value = mock_instance

        cam = CameraFeedHandler()
        cam.get_frame()
        current = cam.get_current_frame()
        assert current is not None
        assert current.shape == (100, 100, 3)

    @patch("cv2.VideoCapture")
    def test_stop(self, mock_vc):
        from camera_feed_handler import CameraFeedHandler

        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = True
        mock_vc.return_value = mock_instance

        cam = CameraFeedHandler()
        cam.start()
        cam.stop()
        mock_instance.release.assert_called_once()
        assert cam.cap is None

    @patch("cv2.VideoCapture")
    def test_stop_without_start(self, mock_vc):
        from camera_feed_handler import CameraFeedHandler

        cam = CameraFeedHandler()
        cam.stop()
        assert cam.cap is None
