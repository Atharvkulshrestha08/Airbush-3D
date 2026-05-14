import cv2
import numpy as np


class CameraFeedHandler:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None
        self.current_frame = None

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")

    def get_frame(self) -> np.ndarray:
        if self.cap is None:
            self.start()

        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to capture frame")

        frame = cv2.flip(frame, 1)
        self.current_frame = frame
        return frame

    def get_current_frame(self) -> np.ndarray:
        return self.current_frame

    def stop(self):
        if self.cap:
            self.cap.release()
            self.cap = None
