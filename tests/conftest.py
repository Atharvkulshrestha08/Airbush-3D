import sys
import os
import cv2
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _draw_and_get_contour(points, thickness=2):
    canvas = np.zeros((400, 400), dtype=np.uint8)
    pts = np.array(points, dtype=np.int32)
    cv2.polylines(canvas, [pts], True, 255, thickness=thickness)
    contours, _ = cv2.findContours(canvas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return max(contours, key=cv2.contourArea) if contours else None


@pytest.fixture
def blank_canvas():
    return np.full((480, 640, 3), 255, dtype=np.uint8)


@pytest.fixture
def sample_contour_rectangle():
    return _draw_and_get_contour([[50, 50], [200, 50], [200, 150], [50, 150]])


@pytest.fixture
def sample_contour_triangle():
    return _draw_and_get_contour([[100, 50], [300, 250], [50, 250]])


@pytest.fixture
def sample_contour_circle():
    angles = np.linspace(0, 2 * np.pi, 60)
    pts = np.array(
        [(100 + 80 * np.cos(a), 100 + 80 * np.sin(a)) for a in angles],
        dtype=np.int32,
    )
    return _draw_and_get_contour(pts, thickness=1)
