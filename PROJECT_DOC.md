# AirBrush Studio - Project Documentation

## Overview
Hand-tracking drawing application with ML-powered features using MediaPipe + OpenCV + PyQt5 + scikit-learn

## Files
- `ui_controller.py` - Main PyQt5 GUI window
- `hand_tracker.py` - MediaPipe hand landmark detection & gesture recognition (supports dual-hand)
- `drawing_engine.py` - Canvas drawing (lines, eraser, highlighter, brush)
- `drawing_mode.py` - Enum for drawing modes
- `camera_feed_handler.py` - Camera capture
- `hand_landmarker.task` - MediaPipe model file
- `ml_recognizer.py` - ML models for digit/shape recognition

## Dependencies
```
pip install opencv-python mediapipe PyQt5 scikit-learn joblib
```

## Running
```bash
python ui_controller.py
```

## Features

### Hand Tracking & Drawing
| Gesture | Fingers | Mode |
|---------|---------|------|
| Pen | Index only | Draws red lines (thickness 5) |
| Eraser | None (fist) | Erases to white (thickness 30) |
| Highlighter | Index + Middle | Yellow lines (thickness 30) |
| Brush | Thumb + Index | Orange lines (thickness 15) |

### Shape Drawing (Dual Hand)
Use index fingers of both hands as vertices:
- Select shape from dropdown (Rectangle, Circle, Triangle)
- Show both hands with index finger extended
- Shape is drawn when hands are positioned

### ML Features
- **Digit Recognition**: Uses SVM trained on MNIST dataset (94.85% accuracy) to recognize handwritten digits
- **Shape Recognition**: Uses contour analysis to detect shapes (Square, Rectangle, Triangle, Circle)

## UI Controls
- Mode display showing current gesture
- Shape mode dropdown for dual-hand drawing
- ML mode selector (None, Digit Recognition, Shape Recognition)
- Clear Canvas button
- Export Image button (saves as PNG)

## Known Issues / To Do
- Smoothing helps with jitter but may need tuning
- Gesture detection may trigger too quickly - could add delay/verification
- No color picker UI yet

## Key Code Locations
- Gesture detection: `hand_tracker.py:40` (detect_gesture method)
- Dual-hand shape drawing: `ui_controller.py:255-298`
- ML digit recognition: `ml_recognizer.py:18-65`
- ML shape recognition: `ml_recognizer.py:68-85`

## Credits
- Built with OpenCode AI assistance
- Prompt Engineering for feature development