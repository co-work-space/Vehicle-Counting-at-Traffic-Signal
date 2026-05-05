from src.tracking.centroid_tracker import CentroidTracker

def test_tracking():
    tracker = CentroidTracker()

    # Simulated detections (x1, y1, x2, y2)
    detections = [
        (100, 100, 150, 150),
        (300, 300, 350, 350)
    ]

    objects = tracker.update(detections)

    print("Tracking test ran successfully")
    print("Tracked objects:", objects)


if __name__ == "__main__":
    test_tracking()