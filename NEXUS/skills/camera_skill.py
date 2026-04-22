"""skills/camera_skill.py"""
import os
from datetime import datetime

class CameraSkill:
    def __init__(self):
        os.makedirs("assets/photos", exist_ok=True)
        self._model = None

    def _get_model(self):
        if not self._model:
            try:
                from ultralytics import YOLO
                self._model = YOLO("yolov8n.pt")
            except Exception as e:
                print(f"[Camera] YOLO load failed: {e}")
        return self._model

    def take_photo(self, q="") -> str:
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if not cap.isOpened(): return "Camera not accessible."
            ret, frame = cap.read(); cap.release()
            if ret:
                fp = f"assets/photos/photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(fp, frame)
                return f"Photo saved: {fp}"
            return "Failed to capture photo."
        except Exception as e: return f"Camera error: {e}"

    def detect_objects(self, q="") -> str:
        try:
            import cv2
            model = self._get_model()
            if not model: return "Detection model unavailable."
            cap = cv2.VideoCapture(0)
            if not cap.isOpened(): return "Camera not accessible."
            ret, frame = cap.read(); cap.release()
            if not ret: return "Could not capture frame."
            results = model(frame)
            detected = list({model.names[int(b.cls[0])] for r in results for b in r.boxes if float(b.conf[0])>0.5})
            return f"Detected: {', '.join(detected)}" if detected else "No objects detected."
        except Exception as e: return f"Detection failed: {e}"
