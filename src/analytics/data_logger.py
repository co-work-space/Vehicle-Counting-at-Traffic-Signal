import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DataLogger:
    """Logs events and exports them to CSV."""
    
    def __init__(self, output_dir="data/outputs"):
        self.output_dir = Path(output_dir)
        # Create the output folder if it doesn't exist yet
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.history = []

    def log_event(self, event_data):
        """Saves a single crossing event into our history list."""
        self.history.append(event_data)

    def export_to_csv(self, filename="traffic_report.csv"):
        """Converts the history into a Pandas DataFrame and saves it as a CSV file."""
        if not self.history:
            logger.warning("No data to export!")
            return None
        
        df = pd.DataFrame(self.history)
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)
        logger.info(f"Data exported successfully to {output_path}")
        return output_path