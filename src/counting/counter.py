import logging
from datetime import datetime
from src.counting.line_crossing import LineCrossingDetector

logger = logging.getLogger(__name__)

class VehicleCounter:
    """Maintains separate counts by direction and vehicle type."""
    
    def __init__(self):
        self.line_detector = LineCrossingDetector()
        self.count_forward = 0
        self.count_backward = 0
        self.count_by_type = {'car': 0, 'truck': 0, 'bus': 0, 'motorcycle': 0}
        self.crossing_events = [] # For the analytics module later!

    def configure_line(self, line_config):
        if line_config['type'] == 'horizontal':
            x_min, x_max = line_config['range']
            self.line_detector.set_horizontal_line(line_config['position'], x_min, x_max)

    def update(self, tracked_objects):
        for objectID, obj_data in tracked_objects.items():
            centroid = obj_data.get('centroid')
            detection = obj_data.get('detection', {})
            
            if centroid is None: 
                continue

            # Check if this specific vehicle crossed the line
            crossing = self.line_detector.is_crossing(objectID, tuple(centroid))
            
            if crossing:
                vehicle_type = detection.get('class_name', 'car')
                
                # Update our scoreboards
                if crossing == 'forward':
                    self.count_forward += 1
                    self.count_by_type[vehicle_type] = self.count_by_type.get(vehicle_type, 0) + 1
                elif crossing == 'backward':
                    self.count_backward += 1
                
                # Log the event for the Analytics Dashboard
                event = {
                    'timestamp': datetime.now(),
                    'objectID': objectID,
                    'direction': crossing,
                    'vehicle_type': vehicle_type
                }
                self.crossing_events.append(event)
                logger.info(f"Crossing detected: ID={objectID}, Type={vehicle_type}, Dir={crossing}")

    def get_counts(self):
        return {
            'total': self.count_forward + self.count_backward,
            'forward': self.count_forward,
            'backward': self.count_backward,
            'by_type': self.count_by_type
        }