"""
MultiCam AI - Vehicle Detection Engine
Supports Ultralytics YOLO with automatic high-speed OpenCV fallback.
Detects: car, motorcycle, bus, truck, and auto-rickshaw.
"""

import os
import cv2
import numpy as np

class VehicleDetection:
    def __init__(self, bbox, class_name, confidence, crop, color_name="#777777"):
        self.bbox = bbox  # (x, y, w, h)
        self.class_name = class_name
        self.confidence = float(confidence)
        self.crop = crop
        self.color_name = color_name

    def to_dict(self):
        return {
            "bbox": self.bbox,
            "class_name": self.class_name,
            "confidence": round(self.confidence, 3),
            "color_name": self.color_name
        }


class HybridVehicleDetector:
    """
    Robust multi-class vehicle detector:
    1. Attempts Ultralytics YOLO if available.
    2. Gracefully falls back to high-performance OpenCV MOG2 + Morphological Contour Analyzer.
    """
    def __init__(self, min_area=400, max_area=180000, conf_threshold=0.35):
        self.min_area = min_area
        self.max_area = max_area
        self.conf_threshold = conf_threshold
        self.yolo_model = None
        self.engine_name = "OpenCV Mixed-Traffic Analyzer"
        self.prev_frame_gray = None

        # Check if Ultralytics is available
        try:
            from ultralytics import YOLO
            model_path = os.path.join(os.path.dirname(__file__), "yolov8n.pt")
            if os.path.exists(model_path):
                self.yolo_model = YOLO(model_path)
                self.engine_name = "Ultralytics YOLOv8"
            else:
                self.engine_name = "OpenCV Mixed-Traffic Analyzer (YOLO Ready)"
        except Exception:
            self.engine_name = "OpenCV Mixed-Traffic Analyzer"

        # Initialize background subtractor for OpenCV engine
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=120, varThreshold=16, detectShadows=True
        )

    def reset(self):
        """Resets the background model and temporal state for a fresh video or stream."""
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=120, varThreshold=16, detectShadows=True
        )
        self.prev_frame_gray = None

    def detect(self, frame, is_night_mode=False):
        """
        Executes vehicle detection on the given frame.
        Returns list of VehicleDetection instances.
        """
        if frame is None or frame.size == 0:
            return []

        # Night mode low-light contrast enhancement
        if is_night_mode:
            frame = self._enhance_night_frame(frame)

        # 1. YOLO Engine
        if self.yolo_model is not None:
            try:
                return self._detect_yolo(frame)
            except Exception as e:
                # Fallback to OpenCV if YOLO throws runtime error
                pass

        # 2. OpenCV Fallback Engine
        return self._detect_opencv(frame)

    def _detect_yolo(self, frame):
        detections = []
        # Class IDs in COCO: 2: car, 3: motorcycle, 5: bus, 7: truck
        yolo_classes = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
        results = self.yolo_model(frame, conf=self.conf_threshold, verbose=False)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0].item())
                if cls_id in yolo_classes:
                    conf = float(box.conf[0].item())
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    w, h = max(1, x2 - x1), max(1, y2 - y1)
                    crop = frame[max(0, y1):min(frame.shape[0], y2), max(0, x1):min(frame.shape[1], x2)]
                    class_name = yolo_classes[cls_id]

                    # Auto-rickshaw refinement in Indian traffic
                    if class_name == "car" and w < 60 and h < 70:
                        # Check high yellow/green saturation characteristic of auto-rickshaws
                        if self._is_auto_rickshaw(crop):
                            class_name = "auto-rickshaw"

                    detections.append(VehicleDetection(
                        bbox=(x1, y1, w, h),
                        class_name=class_name,
                        confidence=conf,
                        crop=crop
                    ))
        return detections

    def _detect_opencv(self, frame):
        detections = []
        h, w = frame.shape[:2]
        frame_area = float(h * w)

        # Dynamic area bounds responsive to video resolution
        dynamic_min_area = max(350, int(0.0006 * frame_area))
        dynamic_max_area = int(0.35 * frame_area)

        # Preprocessing: Grayscale & Gaussian blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # 1. Background subtraction with dynamic learning rate
        fg_mask = self.bg_subtractor.apply(frame, learningRate=0.03)
        _, fg_thresh = cv2.threshold(fg_mask, 180, 255, cv2.THRESH_BINARY)

        # 2. Inter-frame difference (detects instant vehicle motion on frame 1/2)
        if self.prev_frame_gray is not None and self.prev_frame_gray.shape == gray_blur.shape:
            frame_diff = cv2.absdiff(gray_blur, self.prev_frame_gray)
            _, diff_thresh = cv2.threshold(frame_diff, 18, 255, cv2.THRESH_BINARY)
            motion_mask = cv2.bitwise_or(fg_thresh, diff_thresh)
        else:
            motion_mask = fg_thresh

        self.prev_frame_gray = gray_blur

        # Morphological operations to bridge vehicle chassis, roof and bumper
        kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask_clean = cv2.morphologyEx(motion_mask, cv2.MORPH_CLOSE, kernel_close, iterations=2)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, kernel_open, iterations=1)

        # Contour extraction
        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        raw_boxes = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if dynamic_min_area <= area <= dynamic_max_area:
                x, y, bw, bh = cv2.boundingRect(cnt)
                aspect = float(bw) / float(bh)
                # Keep realistic vehicle aspect ratios (0.35 to 3.8)
                if 0.30 <= aspect <= 3.8 and bw >= 18 and bh >= 18:
                    raw_boxes.append((x, y, bw, bh, area))

        # Merge adjacent or split vehicle boxes
        merged_boxes = self._merge_adjacent_boxes(raw_boxes)

        for x, y, bw, bh in merged_boxes:
            crop = frame[max(0, y):min(h, y+bh), max(0, x):min(w, x+bw)]
            if crop.size == 0:
                continue

            aspect_ratio = float(bw) / float(bh)
            area = bw * bh
            class_name, confidence = self._classify_contour(crop, bw, bh, aspect_ratio, area)

            detections.append(VehicleDetection(
                bbox=(x, y, bw, bh),
                class_name=class_name,
                confidence=confidence,
                crop=crop
            ))
        return detections

    def _merge_adjacent_boxes(self, raw_boxes):
        """Merges fragmented vehicle bounding boxes (e.g. cabin + bonnet)."""
        if not raw_boxes:
            return []
        
        boxes = [list(b[:4]) for b in raw_boxes]
        merged = []
        used = [False] * len(boxes)

        for i in range(len(boxes)):
            if used[i]:
                continue
            x1, y1, w1, h1 = boxes[i]
            cur_box = [x1, y1, x1 + w1, y1 + h1]
            used[i] = True

            changed = True
            while changed:
                changed = False
                for j in range(len(boxes)):
                    if used[j]:
                        continue
                    x2, y2, w2, h2 = boxes[j]
                    bx2 = [x2, y2, x2 + w2, y2 + h2]

                    # Check intersection or proximity within 14px
                    inter_x1 = max(cur_box[0], bx2[0])
                    inter_y1 = max(cur_box[1], bx2[1])
                    inter_x2 = min(cur_box[2], bx2[2])
                    inter_y2 = min(cur_box[3], bx2[3])

                    is_close = False
                    if inter_x1 < inter_x2 and inter_y1 < inter_y2:
                        is_close = True
                    else:
                        dx = max(0, max(cur_box[0] - bx2[2], bx2[0] - cur_box[2]))
                        dy = max(0, max(cur_box[1] - bx2[3], bx2[1] - cur_box[3]))
                        if dx < 14 and dy < 14:
                            is_close = True

                    if is_close:
                        cur_box = [
                            min(cur_box[0], bx2[0]),
                            min(cur_box[1], bx2[1]),
                            max(cur_box[2], bx2[2]),
                            max(cur_box[3], bx2[3])
                        ]
                        used[j] = True
                        changed = True

            merged.append((cur_box[0], cur_box[1], cur_box[2] - cur_box[0], cur_box[3] - cur_box[1]))
        return merged

    def _classify_contour(self, crop, w, h, aspect_ratio, area):
        """Classifies vehicle into car, motorcycle, bus, truck, or auto-rickshaw."""
        # 1. Motorcycle / Bike: Slim vertical aspect ratio
        if aspect_ratio < 0.65 and area < 4500:
            return "motorcycle", 0.86

        # 2. Bus / Heavy Commercial: Large area and tall profile
        if area > 14000:
            if aspect_ratio < 0.9 or h > 90:
                return "bus", 0.89
            return "truck", 0.85

        # 3. Auto-Rickshaw (3-Wheeler): Compact, high yellow/green or canvas roof
        if self._is_auto_rickshaw(crop):
            return "auto-rickshaw", 0.88

        # 4. Commercial Truck: Medium-large boxy profile
        if 8000 <= area <= 14000 and aspect_ratio > 1.1:
            return "truck", 0.82

        # 5. Default / Common Fleet: Car (Hatchback/Sedan/SUV)
        return "car", 0.91

    def _is_auto_rickshaw(self, crop):
        """Detects distinctive yellow/green/black coloration of Indian auto-rickshaws."""
        if crop is None or crop.size == 0:
            return False
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        h = hsv[:, :, 0]
        s = hsv[:, :, 1]
        v = hsv[:, :, 2]
        # Yellow hue range: ~20-35 with moderate-high saturation
        yellow_mask = (h >= 20) & (h <= 38) & (s > 60) & (v > 60)
        # Green hue range: ~38-80
        green_mask = (h >= 40) & (h <= 85) & (s > 60) & (v > 50)
        pct_color = (np.sum(yellow_mask) + np.sum(green_mask)) / float(crop.shape[0] * crop.shape[1])
        return pct_color > 0.12

    def _enhance_night_frame(self, frame):
        """Applies CLAHE on luminance channel for night/low-light surveillance footage."""
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        enhanced_lab = cv2.merge((cl, a, b))
        return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
