"""
Vehicle Detection & Frame Analysis Module
Extracts vehicle bounding boxes using background subtraction and contour analysis.
Extracts vehicle crops and annotates frames with tracking IDs and telemetry.
"""

import cv2
import numpy as np
import base64
from core.feature_extractor import extract_vehicle_features


def image_to_base64(img_bgr, quality=80):
    """Encodes a BGR OpenCV image into a JPEG base64 data URI."""
    if img_bgr is None or img_bgr.size == 0:
        return ""
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    success, buffer = cv2.imencode(".jpg", img_bgr, encode_params)
    if not success:
        return ""
    b64_str = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"


class VehicleDetector:
    def __init__(self, min_area=1200, max_area=95000):
        self.min_area = min_area
        self.max_area = max_area
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=200,
            varThreshold=36,
            detectShadows=True
        )

    def detect_in_frame(self, frame_bgr):
        """
        Detects vehicle candidate regions in a single frame.
        Returns a list of dicts: [{'bbox': (x, y, w, h), 'crop': bgr_img, 'features': {...}}]
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return []

        fg_mask = self.bg_subtractor.apply(frame_bgr)
        # Filter out shadows (shadows are marked as 127 in MOG2)
        _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        # Morphological noise removal
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        cleaned = cv2.dilate(cleaned, kernel, iterations=1)

        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections = []

        h_img, w_img = frame_bgr.shape[:2]

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if self.min_area <= area <= self.max_area:
                x, y, w, h = cv2.boundingRect(cnt)
                # Aspect ratio filter for realistic vehicle silhouettes
                aspect = float(w) / float(h)
                if 0.5 <= aspect <= 3.5:
                    # Clip boundaries
                    x1 = max(0, x)
                    y1 = max(0, y)
                    x2 = min(w_img, x + w)
                    y2 = min(h_img, y + h)

                    crop = frame_bgr[y1:y2, x1:x2].copy()
                    features = extract_vehicle_features(crop)
                    if features:
                        detections.append({
                            "bbox": (x1, y1, x2 - x1, y2 - y1),
                            "crop": crop,
                            "features": features
                        })

        return detections


def annotate_frame(frame_bgr, active_tracklets, camera_id="CAM-A", timestamp_str="14:02:15"):
    """
    Renders an engineering overlay onto a video frame:
    - Bounding boxes with corner brackets
    - Track ID badges
    - Vehicle type and dominant color label
    - Camera ID and timestamp watermark
    """
    canvas = frame_bgr.copy()
    h, w = canvas.shape[:2]

    # Draw camera header HUD bar
    cv2.rectangle(canvas, (0, 0), (w, 34), (15, 23, 42), -1)
    cv2.putText(
        canvas,
        f"{camera_id} - LIVE RTSP FEED | UTC {timestamp_str} | NON-OVERLAPPING SURVEILLANCE",
        (12, 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (220, 230, 240),
        1,
        cv2.LINE_AA
    )

    # Draw each active vehicle bounding box
    for track in active_tracklets:
        if not track.bboxes:
            continue
        x, y, bw, bh = track.bboxes[-1]
        t_id = track.track_id
        v_type = track.features.get("vehicle_type", "Vehicle") if track.features else "Vehicle"
        col_name = track.features.get("dominant_color_name", "") if track.features else ""

        # Engineering styling: high-contrast slate-blue box
        box_color = (255, 180, 50) if "CAM-A" in camera_id else (50, 200, 255)
        cv2.rectangle(canvas, (x, y), (x + bw, y + bh), box_color, 2)

        # Label tag
        label = f"[{t_id}] {col_name} {v_type}"
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        cv2.rectangle(canvas, (x, y - lh - 8), (x + lw + 8, y), (15, 23, 42), -1)
        cv2.rectangle(canvas, (x, y - lh - 8), (x + lw + 8, y), box_color, 1)
        cv2.putText(canvas, label, (x + 4, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

    return canvas
