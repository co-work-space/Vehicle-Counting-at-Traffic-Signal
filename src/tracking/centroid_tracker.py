import numpy as np
from scipy.spatial import distance as dist
from src.utils.config import MAX_DISAPPEARED

class CentroidTracker:
    """Tracks objects across video frames by matching center point distances."""
    
    def __init__(self, max_distance=50):
        self.next_object_id = 0
        self.objects = {}       # Dictionary: {object_id: centroid_coordinates}
        self.disappeared = {}   # Tracks how many frames an object has been missing
        self.max_distance = max_distance
        self.classes = {}       # Dictionary: {object_id: class_name_string}

    def register(self, centroid, class_name):
        """Registers a new vehicle when it enters the frame."""
        self.objects[self.next_object_id] = tuple(centroid)
        self.disappeared[self.next_object_id] = 0
        self.classes[self.next_object_id] = class_name
        self.next_object_id += 1

    def deregister(self, object_id):
        """Removes a vehicle from tracking if it leaves the frame."""
        del self.objects[object_id]
        del self.disappeared[object_id]
        del self.classes[object_id]

    def update(self, rects_with_classes):
        """Matches new bounding box detections to existing tracked vehicles."""
        if len(rects_with_classes) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > MAX_DISAPPEARED:
                    self.deregister(object_id)
            return self.get_tracked_dict()

        # Extract centroids and labels
        input_centroids = np.zeros((len(rects_with_classes), 2), dtype="int")
        input_classes = []
        
        for i, (x1, y1, x2, y2, class_name) in enumerate(rects_with_classes):
            cx = int((x1 + x2) / 2.0)
            cy = int((y1 + y2) / 2.0)
            input_centroids[i] = (cx, cy)
            input_classes.append(class_name)

        if len(self.objects) == 0:
            for i in range(0, len(input_centroids)):
                self.register(input_centroids[i], input_classes[i])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            # Calculate Euclidean distance between points
            D = dist.cdist(np.array(object_centroids), input_centroids)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                if D[row, col] > self.max_distance:
                    continue

                object_id = object_ids[row]
                self.objects[object_id] = tuple(input_centroids[col])
                self.disappeared[object_id] = 0
                self.classes[object_id] = input_classes[col]

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)

            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > MAX_DISAPPEARED:
                    self.deregister(object_id)

            for col in unused_cols:
                self.register(input_centroids[col], input_classes[col])

        return self.get_tracked_dict()

    def get_tracked_dict(self):
        """Formats data cleanly for dashboard widgets."""
        tracked_objects = {}
        for obj_id, centroid in self.objects.items():
            tracked_objects[obj_id] = {
                'centroid': centroid,
                'detection': {'class_name': self.classes[obj_id]}
            }
        return tracked_objects