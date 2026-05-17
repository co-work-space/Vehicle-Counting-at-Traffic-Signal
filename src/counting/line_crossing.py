import numpy as np
import logging

logger = logging.getLogger(__name__)

class LineCrossingDetector:
    """Detect when objects cross virtual lines using geometric cross products."""
    
    def __init__(self):
        self.centroid_history = {} # Keeps track of where the car was in the last frame

    def set_line(self, x1, y1, x2, y2):
        self.line_start = (x1, y1)
        self.line_end = (x2, y2)
        logger.info(f"Line set: ({x1},{y1}) to ({x2},{y2})")

    def set_horizontal_line(self, y_pos, x_min=0, x_max=640):
        self.set_line(x_min, y_pos, x_max, y_pos)

    def point_to_line_side(self, point):
        """Math magic: Cross product determines which side of the line the point is on."""
        x, y = point
        x1, y1 = self.line_start
        x2, y2 = self.line_end
        return (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)

    def is_crossing(self, objectID, new_centroid):
        """Checks if the car's sign (+/-) changed compared to the line since the last frame."""
        # If it's a new car, just save its position and wait for the next frame
        if objectID not in self.centroid_history:
            self.centroid_history[objectID] = [new_centroid]
            return None

        previous_centroid = self.centroid_history[objectID][-1]
        old_side = self.point_to_line_side(previous_centroid)
        new_side = self.point_to_line_side(new_centroid)

        self.centroid_history[objectID].append(new_centroid)
        
        # Keep history small to save memory
        if len(self.centroid_history[objectID]) > 5:
            self.centroid_history[objectID] = self.centroid_history[objectID][-5:]

        # If old_side and new_side have different signs, they multiply to a negative number = CROSSING!
        if old_side * new_side < 0: 
            if old_side < 0:
                return 'forward'
            else:
                return 'backward'
                
        return None