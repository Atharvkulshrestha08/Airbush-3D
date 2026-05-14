import numpy as np
import cv2
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os


class DigitRecognizer:
    def __init__(self):
        self.model = None
        self.scaler = None
        self._load_or_train_model()

    def _load_or_train_model(self):
        model_path = "digit_model.pkl"
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            self.scaler = joblib.load("scaler.pkl")
            return

        print("Loading MNIST dataset...")
        try:
            X, y = fetch_openml("mnist_784", version=1, return_X_y=True, as_frame=False)
            y = y.astype(int)

            X = X[:10000]
            y = y[:10000]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)

            print("Training digit recognition model...")
            self.model = SVC(kernel="rbf", C=10, gamma="scale")
            self.model.fit(X_train_scaled, y_train)

            accuracy = self.model.score(self.scaler.transform(X_test), y_test)
            print(f"Model accuracy: {accuracy:.2%}")

            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, "scaler.pkl")
        except Exception as e:
            print(f"Could not train model: {e}")
            self.model = None

    def recognize_digit(self, image):
        if image is None or image.size == 0 or self.model is None:
            return None

        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )

        coords = np.column_stack(np.where(gray > 200))
        if len(coords) == 0:
            return None

        y, x, h, w = cv2.boundingRect(coords)

        margin = 5
        x = max(0, x - margin)
        y = max(0, y - margin)
        w = min(gray.shape[1] - x, w + 2 * margin)
        h = min(gray.shape[0] - y, h + 2 * margin)

        digit_roi = gray[y : y + h, x : x + w]

        if w == 0 or h == 0:
            return None

        resized = cv2.resize(digit_roi, (28, 28))
        normalized = resized.flatten().astype("float32") / 255.0

        scaled = self.scaler.transform([normalized])
        prediction = self.model.predict(scaled)

        return str(prediction[0])


class ShapeRecognizer:
    def __init__(self):
        pass

    def recognize_shape_from_points(self, points):
        if not points or len(points) < 5:
            return "Unknown"
        contour = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        # Ensure the contour is closed for arcLength
        if np.linalg.norm(contour[0][0] - contour[-1][0]) > 20: 
            # If the ends are far apart, it's probably an open stroke, but we can try to close it or handle it
            pass
        return self.recognize_shape(contour)

    def recognize_shape(self, contour):
        if contour is None or len(contour) < 5:
            return "Unknown"

        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h if h != 0 else 0
            if 0.9 <= aspect_ratio <= 1.1:
                return "Square"
            return "Rectangle"
        elif len(approx) == 3:
            return "Triangle"
        elif len(approx) > 6:
            return "Circle"

        return "Unknown"
