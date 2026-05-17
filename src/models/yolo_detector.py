from ultralytics import YOLO
import cv2

from src.utils.config import CONF_THRESHOLD, MODEL_NAME
from src.detection.preprocessing import resize_frame


class YOLODetector:
    def __init__(self):
        print("[INFO] Loading YOLO model...")
        self.model = YOLO(MODEL_NAME)

    def detect(self, frame):
        # Optional preprocessing (resize for speed)
        frame = resize_frame(frame)

        results = self.model(frame)
        detections = []

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])

                # Filter only vehicles
                # 2=car, 3=motorcycle, 5=bus, 7=truck, 8=Auto-rickshaw
                if conf > CONF_THRESHOLD and cls in [2, 3, 5, 7, 8]:
                    detections.append({
                        "bbox": (x1, y1, x2, y2),
                        "confidence": conf,
                        "class": cls
                    })

        return detections

    def draw_detections(self, frame, detections):
        for d in detections:
            x1, y1, x2, y2 = d["bbox"]
            conf = d["confidence"]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"{conf:.2f}",
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        return frame

    def get_centroid(self, detection):
        x1, y1, x2, y2 = detection["bbox"]
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        return (cx, cy)