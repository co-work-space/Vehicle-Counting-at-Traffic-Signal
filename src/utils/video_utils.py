import cv2

def draw_boxes(frame, detections):
    for d in detections:
        x1, y1, x2, y2 = d["bbox"]
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
    return frame

def draw_ids(frame, objects):
    for obj_id, centroid in objects.items():
        cv2.putText(frame, f"ID {obj_id}", centroid,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
    return frame