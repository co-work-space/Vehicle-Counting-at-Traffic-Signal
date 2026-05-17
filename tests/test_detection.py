from src.models.yolo_detector import YOLODetector

def test_detection():
    detector = YOLODetector()

    # Create a dummy frame (black image)
    import numpy as np
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    detections = detector.detect(frame)

    print("Detection test ran successfully")
    print("Detections:", detections)


if __name__ == "__main__":
    test_detection()