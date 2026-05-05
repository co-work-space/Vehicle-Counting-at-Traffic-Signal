import numpy as np
from src.utils.config import MAX_DISAPPEARED


class CentroidTracker:
    def __init__(self):
        self.next_object_id = 0
        self.objects = {}
        self.disappeared = {}

    def register(self, centroid):
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, boxes):
        # No detections case
        if len(boxes) == 0:
            for obj_id in list(self.disappeared.keys()):
                self.disappeared[obj_id] += 1

                if self.disappeared[obj_id] > MAX_DISAPPEARED:
                    self.deregister(obj_id)

            return self.objects

        # Compute centroids
        input_centroids = np.array([
            ((x1 + x2) // 2, (y1 + y2) // 2)
            for (x1, y1, x2, y2) in boxes
        ])

        # If no existing objects
        if len(self.objects) == 0:
            for centroid in input_centroids:
                self.register(centroid)

        else:
            object_ids = list(self.objects.keys())
            self.objects = {
                obj_id: tuple(c)
                for obj_id, c in zip(object_ids, input_centroids)
            }

        return self.objects