import cv2

def resize_frame(frame, max_width=800):
    h, w = frame.shape[:2]
    if w > max_width:
        scale = max_width / w
        frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
    return frame


def apply_blur_denoise(frame, strength=5):
    return cv2.GaussianBlur(frame, (strength, strength), 0)


def apply_histogram_equalization(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    equalized = cv2.equalizeHist(gray)
    return cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)


def apply_brightness_contrast(frame, brightness=0, contrast=0):
    beta = brightness
    alpha = 1 + (contrast / 100.0)

    adjusted = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
    return adjusted