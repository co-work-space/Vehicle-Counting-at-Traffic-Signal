from src.tracking.centroid_tracker import CentroidTracker


class TrackerManager:
    def __init__(self):
        self.tracker = CentroidTracker()

    def update(self, detections):
        # Extract bounding boxes from detection dict
        boxes = [d["bbox"] for d in detections]

        # Update tracker
        objects = self.tracker.update(boxes)

        return objects