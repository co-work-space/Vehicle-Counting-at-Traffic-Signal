import numpy as np

class TrafficAnalytics:
    """Calculates advanced metrics from raw traffic data."""
    
    def __init__(self, frame_width=640, frame_height=480):
        self.frame_area = frame_width * frame_height

    def calculate_density(self, current_count):
        """Density = number of vehicles / frame area."""
        # We multiply by 1000 just to make it a readable decimal for the dashboard
        return (current_count / self.frame_area) * 1000 

    def get_statistics_by_vehicle_type(self, counts_by_type):
        """Returns the percentage distribution of vehicle types (e.g., 80% cars, 20% trucks)."""
        total = sum(counts_by_type.values())
        if total == 0:
            return {k: 0.0 for k in counts_by_type}
        return {k: round((v / total) * 100, 2) for k, v in counts_by_type.items()}
    
    def generate_report(self, counter_data):
        """Compiles current stats into a single dictionary package for the dashboard."""
        return {
            "total_count": counter_data['total'],
            "forward_traffic": counter_data['forward'],
            "backward_traffic": counter_data['backward'],
            "density": self.calculate_density(counter_data['total']),
            "distribution": self.get_statistics_by_vehicle_type(counter_data['by_type'])
        }