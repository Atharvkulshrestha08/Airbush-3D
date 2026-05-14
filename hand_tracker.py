import math
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np
import os
from collections import Counter


class HandTracker:
    def __init__(self):
        base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
        options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.prev_gesture = "none"
        self.gesture_history = []
        self.history_size = 10

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        results = self.detector.detect(mp_image)
        return results

    def get_index_finger_tip(
        self, results, frame_shape, prev_pos=None, hand_was_lost=False
    ):
        if not results or not results.hand_landmarks:
            return None

        h, w = frame_shape[:2]
        landmarks = results.hand_landmarks[0]

        tip = landmarks[8]
        x, y = int(tip.x * w), int(tip.y * h)

        if prev_pos is not None and hand_was_lost:
            dist = ((x - prev_pos[0]) ** 2 + (y - prev_pos[1]) ** 2) ** 0.5
            if dist > 150:
                return prev_pos

        return (x, y)

    def _is_thumb_extended(self, landmarks):
        index_mcp = landmarks[5]
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        dt = (
            (thumb_tip.x - index_mcp.x) ** 2 + (thumb_tip.y - index_mcp.y) ** 2
        ) ** 0.5
        di = ((thumb_ip.x - index_mcp.x) ** 2 + (thumb_ip.y - index_mcp.y) ** 2) ** 0.5
        return dt > di

    def detect_gesture(self, results):
        if not results or not results.hand_landmarks:
            self.gesture_history.append("none")
            if len(self.gesture_history) > self.history_size:
                self.gesture_history.pop(0)
            return self._get_stable_gesture()

        landmarks = results.hand_landmarks[0]

        index_ext = landmarks[8].y < landmarks[6].y
        middle_ext = landmarks[12].y < landmarks[10].y
        ring_ext = landmarks[16].y < landmarks[14].y
        pinky_ext = landmarks[20].y < landmarks[18].y
        thumb_ext = self._is_thumb_extended(landmarks)

        ext_count = sum([index_ext, middle_ext, ring_ext, pinky_ext])

        if ext_count >= 4:
            gesture = "eraser"
        elif index_ext and not middle_ext and not ring_ext and not pinky_ext:
            gesture = "pen"
        elif index_ext and middle_ext and not ring_ext and not pinky_ext:
            gesture = "highlighter"
        elif index_ext and middle_ext and ring_ext and not pinky_ext:
            gesture = "brush"
        elif thumb_ext and index_ext and not middle_ext:
            gesture = "brush"
        elif thumb_ext and not index_ext and not middle_ext:
            gesture = "select"
        else:
            gesture = "none"

        self.gesture_history.append(gesture)
        if len(self.gesture_history) > self.history_size:
            self.gesture_history.pop(0)

        return self._get_stable_gesture()

    def _get_stable_gesture(self):
        if len(self.gesture_history) < 3:
            return self.gesture_history[-1] if self.gesture_history else "none"

        counts = Counter(self.gesture_history)
        best = counts.most_common(1)[0]
        gesture, count = best

        if count >= 6:
            self.prev_gesture = gesture
            return gesture

        if count >= 3:
            return gesture

        return self.prev_gesture

    def get_two_hand_positions(self, results, frame_shape):
        if not results or not results.hand_landmarks or len(results.hand_landmarks) < 2:
            return None, None

        h, w = frame_shape[:2]

        hand1_tip = results.hand_landmarks[0][8]
        hand1_thumb = results.hand_landmarks[0][4]

        hand2_tip = results.hand_landmarks[1][8]
        hand2_thumb = results.hand_landmarks[1][4]

        pos1 = (int(hand1_tip.x * w), int(hand1_tip.y * h))
        pos2 = (int(hand2_tip.x * w), int(hand2_tip.y * h))

        return pos1, pos2

    def get_four_point_gesture(self, results, frame_shape):
        if not results or not results.hand_landmarks or len(results.hand_landmarks) < 2:
            return None

        h, w = frame_shape[:2]

        hand1_points = self._get_thumb_index_points(results.hand_landmarks[0], w, h)
        hand2_points = self._get_thumb_index_points(results.hand_landmarks[1], w, h)

        if hand1_points is None or hand2_points is None:
            return None

        return {
            "hand1_index": hand1_points["index"],
            "hand1_thumb": hand1_points["thumb"],
            "hand2_index": hand2_points["index"],
            "hand2_thumb": hand2_points["thumb"],
        }

    def _get_thumb_index_points(self, landmarks, w, h):
        index_tip = landmarks[8]
        thumb_tip = landmarks[4]

        index_extended = index_tip.y < landmarks[6].y
        index_mcp = landmarks[5]
        thumb_ip = landmarks[3]
        dist_tip_to_index = (thumb_tip.x - index_mcp.x) ** 2 + (
            thumb_tip.y - index_mcp.y
        ) ** 2
        dist_ip_to_index = (thumb_ip.x - index_mcp.x) ** 2 + (
            thumb_ip.y - index_mcp.y
        ) ** 2
        thumb_extended = dist_tip_to_index > dist_ip_to_index

        if index_extended and thumb_extended:
            return {
                "index": (int(index_tip.x * w), int(index_tip.y * h)),
                "thumb": (int(thumb_tip.x * w), int(thumb_tip.y * h)),
            }
        return None

    def detect_fist(self, results):
        if not results or not results.hand_landmarks or len(results.hand_landmarks) < 2:
            return False

        for landmarks in results.hand_landmarks:
            fingers = []
            for tip, base in [(8, 6), (12, 10), (16, 14), (20, 18)]:
                tip_landmark = landmarks[tip]
                base_landmark = landmarks[base]
                fingers.append(tip_landmark.y < base_landmark.y)

            extended_count = sum(fingers)
            if extended_count > 1:
                return False

        return True

    def detect_middle_finger_raise(self, results):
        if not results or not results.hand_landmarks or len(results.hand_landmarks) < 2:
            return False

        for landmarks in results.hand_landmarks:
            middle_tip = landmarks[12]
            middle_base = landmarks[10]
            middle_extended = middle_tip.y < middle_base.y
            if not middle_extended:
                return False

        return True

    def get_all_four_points(self, results, frame_shape):
        gesture_data = self.get_four_point_gesture(results, frame_shape)
        if gesture_data is None:
            return None

        return [
            gesture_data["hand1_index"],
            gesture_data["hand1_thumb"],
            gesture_data["hand2_index"],
            gesture_data["hand2_thumb"],
        ]

    def draw_landmarks(self, frame, results):
        if results and results.hand_landmarks:
            for landmarks in results.hand_landmarks:
                for i, landmark in enumerate(landmarks):
                    x, y = (
                        int(landmark.x * frame.shape[1]),
                        int(landmark.y * frame.shape[0]),
                    )
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                connections = [
                    (0, 1),
                    (1, 2),
                    (2, 3),
                    (3, 4),
                    (0, 5),
                    (5, 6),
                    (6, 7),
                    (7, 8),
                    (0, 9),
                    (9, 10),
                    (10, 11),
                    (11, 12),
                    (0, 13),
                    (13, 14),
                    (14, 15),
                    (15, 16),
                    (0, 17),
                    (17, 18),
                    (18, 19),
                    (19, 20),
                    (5, 9),
                    (9, 13),
                    (13, 17),
                ]
                for start, end in connections:
                    x1, y1 = (
                        int(landmarks[start].x * frame.shape[1]),
                        int(landmarks[start].y * frame.shape[0]),
                    )
                    x2, y2 = (
                        int(landmarks[end].x * frame.shape[1]),
                        int(landmarks[end].y * frame.shape[0]),
                    )
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return frame
