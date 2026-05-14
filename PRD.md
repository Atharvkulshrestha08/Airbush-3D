# AirBrush Studio - Product Requirements Document (PRD)

## 1. Project Overview

**Project Name:** AirBrush Studio  
**Project Type:** Hand-tracking drawing application with ML capabilities  
**Core Functionality:** Real-time hand gesture recognition for freehand drawing and shape creation using webcam input  
**Target Users:** AI/ML students, creative professionals, and developers interested in gesture-based interfaces

---

## 2. Current Features

### 2.1 Hand Tracking & Drawing
| Gesture | Fingers Detected | Drawing Mode | Color | Thickness |
|---------|------------------|--------------|-------|-----------|
| Pen | Index only | Draws lines | Red (0,0,255) | 5 |
| Eraser | None (fist/closed) | Erases to white | White (255,255,255) | 30 |
| Highlighter | Index + Middle | Draws lines | Yellow (255,255,0) | 30 |
| Brush | Thumb + Index | Draws lines | Orange (0,165,255) | 15 |

### 2.2 Shape Drawing (Dual-Hand)
- **Trigger:** Index + Thumb extended on BOTH hands (4-finger stretch)
- **Preview:** Shape displayed in real-time while gesture is active
- **Finalization:** Make fist to save shape to canvas
- **Available Shapes:** Rectangle, Circle, Triangle

### 2.3 ML Features
| Feature | Model | Accuracy | Description |
|---------|-------|----------|-------------|
| Digit Recognition | SVM (RBF kernel) | 94.85% | Recognizes handwritten digits from canvas |
| Shape Recognition | Contour Analysis | N/A | Detects shapes: Square, Rectangle, Triangle, Circle |

### 2.4 UI Controls
- Current mode display (Pen/Eraser/Highlighter/Brush/None)
- Gesture detection status
- Shape mode dropdown selector
- ML mode selector (None/Digit Recognition/Shape Recognition)
- Clear Canvas button
- Export Image button (PNG format)

---

## 3. Technical Architecture

### 3.1 File Structure
```
├── ui_controller.py         # Main PyQt5 GUI window
├── hand_tracker.py         # MediaPipe hand landmark detection
├── drawing_engine.py       # Canvas drawing operations
├── drawing_mode.py         # Enum for drawing modes
├── camera_feed_handler.py  # Webcam capture
├── ml_recognizer.py        # ML models (digit & shape recognition)
├── hand_landmarker.task    # MediaPipe model file
├── digit_model.pkl         # Trained SVM model (auto-generated)
├── scaler.pkl              # StandardScaler (auto-generated)
└── PROJECT_DOC.md          # Project documentation
```

### 3.2 Technology Stack
| Component | Technology |
|-----------|------------|
| GUI Framework | PyQt5 |
| Computer Vision | OpenCV |
| Hand Tracking | MediaPipe |
| ML (Digit Recognition) | scikit-learn (SVM) |
| ML (Shape Recognition) | OpenCV contour analysis |

### 3.3 Key Classes & Methods

**HandTracker (hand_tracker.py)**
- `process_frame(frame)` - Detect hands in frame
- `detect_gesture(results)` - Classify single-hand gesture
- `detect_fist(results)` - Check if both hands are in fist position
- `get_all_four_points(results, frame_shape)` - Get positions of both index fingers and thumbs
- `get_four_point_gesture(results, frame_shape)` - Detect 4-finger stretch gesture

**UIController (ui_controller.py)**
- `update_frame()` - Main loop: process frame → detect gesture → draw → update display
- `_draw_shape_preview(points, shape_mode)` - Draw preview shape (green dashed)
- `_finalize_shape(points, shape_mode)` - Draw permanent shape (solid green)
- `_update_display(frame)` - Convert frame to Qt image and display

---

## 4. Shape Recognition - Areas for Improvement

### 4.1 Current Implementation Issues

**Problem 1: Gesture Detection Logic**
- Current: Detects index + thumb extended (4-finger stretch)
- Issue: May be too strict or too lenient depending on hand orientation
- Suggested Improvement: Add tolerance for finger angle variations

**Problem 2: Shape Calculation**
- Current: Uses bounding box of all 4 points
- Issue: Shape doesn't dynamically grow/shrink based on finger spread distance
- Suggested Improvement: Calculate shape based on actual distance between fingers

**Problem 3: Preview Persistence**
- Current: Preview shape accumulates on canvas
- Issue: Should clear previous preview before drawing new one
- Suggested Improvement: Use separate preview layer or clear before each update

**Problem 4: Fist Detection**
- Current: Requires both hands to be closed (only 0-1 fingers extended per hand)
- Issue: May trigger prematurely or miss valid fist gestures
- Suggested Improvement: Add confidence threshold or temporal smoothing

### 4.2 Desired Shape Drawing Behavior

```
User Flow:
1. User selects "Rectangle" from dropdown
2. User shows 4-finger stretch gesture (index + thumb on both hands)
   → System detects gesture and starts preview
3. User spreads fingers apart
   → Rectangle grows in real-time following finger distance
4. User makes fist (both hands closed)
   → Shape is finalized and saved to canvas permanently
5. Preview is cleared, ready for next shape
```

**Expected Behavior:**
- Shape size should be proportional to distance between fingers
- Preview should update at ~30 FPS without accumulating
- Finalization should only occur on clear fist gesture
- Previous preview should not leave artifacts on canvas

### 4.3 Technical Requirements for Improvement

1. **Real-time Finger Distance Calculation**
   - Calculate Euclidean distance between index fingers
   - Use distance as scaling factor for shape dimensions

2. **Preview Layer Management**
   - Option A: Use a separate preview canvas that gets cleared each frame
   - Option B: Store previous preview coordinates and redraw in white before drawing new

3. **Gesture Confidence Scoring**
   - Add threshold-based detection to reduce false positives
   - Consider adding temporal verification (gesture must be stable for N frames)

4. **Improved Shape Geometries**
   - Rectangle: Use finger distance as width/height
   - Circle: Use distance as radius
   - Triangle: Use finger positions as vertices

---

## 5. Non-Functional Requirements

| Requirement | Description |
|-------------|-------------|
| Performance | 30 FPS minimum for smooth real-time drawing |
| Latency | <100ms from gesture to visual feedback |
| Compatibility | Windows 10/11, Python 3.13 |
| Dependencies | opencv-python, mediapipe, PyQt5, scikit-learn, joblib |

---

## 6. Known Limitations

1. No color picker UI - colors are hardcoded
2. Smoothing may need tuning for different lighting conditions
3. Gesture detection may trigger too quickly - could benefit from delay/verification
4. Shape recognition ML model trains on first run (~30 seconds)
5. Requires good lighting for accurate hand tracking

---

## 7. Future Enhancement Ideas

1. Custom color picker for drawing
2. Undo/redo functionality
3. Save/load canvas as project files
4. Voice commands for mode switching
5. Background removal for cleaner canvas
6. Object detection overlay on camera feed
7. Character recognition (A-Z, a-z)
8. Emoji recognition from hand gestures
9. Multi-layer canvas system
10. Touch tablet as secondary input option

---

## 8. Testing Checklist

- [ ] Pen gesture draws red lines
- [ ] Eraser gesture clears to white
- [ ] Highlighter draws yellow semi-transparent lines
- [ ] Brush draws orange lines
- [ ] Shape mode dropdown shows all options
- [ ] 4-finger stretch gesture triggers preview
- [ ] Spreading fingers grows shape in real-time
- [ ] Fist gesture finalizes shape
- [ ] Clear Canvas button works
- [ ] Export Image saves PNG file
- [ ] ML digit recognition identifies numbers
- [ ] ML shape recognition identifies shapes on canvas

---

## 9. Dependencies & Installation

```bash
pip install opencv-python mediapipe PyQt5 scikit-learn joblib
```

**Note:** On first run, the digit recognition model will automatically download MNIST data and train (~30 seconds). Subsequent runs will load the cached model.

---

*Document Version: 1.0*  
*Last Updated: 2026-04-10*  
*Generated for: AirBrush Studio v1.0*