import cv2

class VideoDetectionPipeline:
    def __init__(self, detector):
        self.detector = detector

    def process_video(self, video_path):
        cap = cv2.VideoCapture(video_path)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            detections = self.detector.detect(frame)

            for box in detections:
                x1, y1, x2, y2, _ = box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

            cv2.imshow("Detection", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()