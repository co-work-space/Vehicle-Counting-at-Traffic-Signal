import cv2
from src.models.yolo_detector import YOLODetector
from src.tracking.tracker_manager import TrackerManager
from src.utils.video_utils import draw_boxes, draw_ids
from src.utils.config import SKIP_FRAMES

def run(video_path):
    cap = cv2.VideoCapture(video_path)

    detector = YOLODetector()
    tracker = TrackerManager()

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % SKIP_FRAMES != 0:
            continue

        detections = detector.detect(frame)
        objects = tracker.update(detections)

        frame = draw_boxes(frame, detections)
        frame = draw_ids(frame, objects)

        cv2.imshow("Vehicle Tracking", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run("data/test.mp4")