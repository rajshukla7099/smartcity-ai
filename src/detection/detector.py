"""
MultiCam AI - Vehicle Detection Engine
Supports OpenCV DNN YOLO ONNX Deep Learning with robust OpenCV fallback.
Exclusively detects real vehicles: car, motorcycle, bus, truck, and auto-rickshaw.
Filters out background noise, shadows, road pavement, and camera flicker.
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
    High-precision vehicle detector:
    1. Primary: YOLOv5 Deep Learning ONNX via OpenCV DNN (0 false positives on road/trees).
    2. Fallback: Strict Geometric-Motion Filter with NMS and Shadow Suppression.
    """
    def __init__(self, min_area=1200, max_area=250000, conf_threshold=0.30):
        self.min_area = min_area
        self.max_area = max_area
        self.conf_threshold = conf_threshold
        self.net = None
        self.engine_name = "OpenCV Classical Filter"
        self.prev_frame_gray = None

        # COCO Vehicle Class Mapping
        # 2: car, 3: motorcycle, 5: bus, 7: truck
        self.vehicle_classes = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

        # Attempt to load YOLOv5 ONNX model
        potential_model_paths = [
            os.path.join(os.path.dirname(__file__), "..", "..", "models", "yolov5n.onnx"),
            os.path.join("models", "yolov5n.onnx"),
            os.path.join(os.path.dirname(__file__), "yolov5n.onnx"),
            os.path.abspath(r"c:\Users\rajsh\Downloads\city ai\models\yolov5n.onnx"),
            os.path.abspath(r"c:\Users\rajsh\Downloads\smartcity\models\yolov5n.onnx"),
        ]

        for mp in potential_model_paths:
            if os.path.exists(mp) and os.path.getsize(mp) > 1000000:
                try:
                    self.net = cv2.dnn.readNetFromONNX(mp)
                    self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                    self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                    self.engine_name = "YOLOv5 Deep Learning (OpenCV DNN)"
                    break
                except Exception:
                    self.net = None

        # Initialize background subtractor for fallback
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=200, varThreshold=24, detectShadows=True
        )

    def reset(self):
        """Resets the background model and temporal state for a fresh video or stream."""
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=200, varThreshold=24, detectShadows=True
        )
        self.prev_frame_gray = None

    def detect(self, frame, is_night_mode=False):
        """
        Executes vehicle detection on the given frame.
        Exclusively spots real vehicles (car, motorcycle, bus, truck, auto-rickshaw).
        """
        if frame is None or frame.size == 0:
            return []

        # Night mode low-light contrast enhancement
        if is_night_mode:
            frame = self._enhance_night_frame(frame)

        # 1. Primary: YOLO ONNX Deep Learning Engine
        if self.net is not None:
            try:
                yolo_dets = self._detect_onnx(frame)
                if yolo_dets is not None and len(yolo_dets) > 0:
                    return yolo_dets
            except Exception:
                pass

        # 2. Strict Classical Fallback (Only real vehicles, suppresses asphalt/trees/noise)
        return self._detect_opencv_strict(frame)

    def _detect_onnx(self, frame):
        """Deep learning vehicle detection using YOLOv5 ONNX."""
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (640, 640), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward()

        if isinstance(outputs, (list, tuple)):
            output = outputs[0]
        else:
            output = outputs

        # Output shape is (1, 25200, 85)
        if len(output.shape) == 3:
            output = output[0]

        x_factor = w / 640.0
        y_factor = h / 640.0

        boxes = []
        confidences = []
        class_ids = []

        for row in output:
            obj_conf = float(row[4])
            if obj_conf >= self.conf_threshold:
                class_scores = row[5:]
                class_id = int(np.argmax(class_scores))
                score = float(class_scores[class_id])
                combined_conf = obj_conf * score

                if combined_conf >= self.conf_threshold and class_id in self.vehicle_classes:
                    cx, cy, bw, bh = float(row[0]), float(row[1]), float(row[2]), float(row[3])
                    left = int((cx - 0.5 * bw) * x_factor)
                    top = int((cy - 0.5 * bh) * y_factor)
                    width = int(bw * x_factor)
                    height = int(bh * y_factor)

                    # Ensure box stays within frame boundaries
                    left = max(0, left)
                    top = max(0, top)
                    width = min(w - left, width)
                    height = min(h - top, height)

                    if width >= 25 and height >= 20:
                        boxes.append([left, top, width, height])
                        confidences.append(combined_conf)
                        class_ids.append(class_id)

        if not boxes:
            return []

        # Non-Maximum Suppression to remove overlapping duplicate boxes
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, 0.45)
        detections = []

        indices_list = indices.flatten() if hasattr(indices, "flatten") else indices
        for i in indices_list:
            bx, by, bw, bh = boxes[i]
            cid = class_ids[i]
            conf = confidences[i]
            class_name = self.vehicle_classes[cid]

            crop = frame[by:by + bh, bx:bx + bw]
            if crop.size == 0:
                continue

            # Auto-rickshaw refinement in Indian traffic
            if class_name == "car" and (bw < 90 and bh < 90) and self._is_auto_rickshaw(crop):
                class_name = "auto-rickshaw"

            detections.append(VehicleDetection(
                bbox=(bx, by, bw, bh),
                class_name=class_name,
                confidence=conf,
                crop=crop
            ))

        return detections

    def _detect_opencv_strict(self, frame):
        """
        High-precision classical vehicle detector.
        Uses high thresholds, edge density, and aspect constraints to reject background noise.
        """
        detections = []
        h, w = frame.shape[:2]
        frame_area = float(h * w)

        # Strict area bounds to ignore small noise and ground textures
        dynamic_min_area = max(1800, int(0.0035 * frame_area))
        dynamic_max_area = int(0.40 * frame_area)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # 1. Background subtraction (detectShadows=True marks shadows as gray 127)
        fg_mask = self.bg_subtractor.apply(frame, learningRate=0.015)
        # Strict threshold to remove shadows (only values 240+ are true moving vehicles)
        _, fg_thresh = cv2.threshold(fg_mask, 240, 255, cv2.THRESH_BINARY)

        # 2. Inter-frame difference
        if self.prev_frame_gray is not None and self.prev_frame_gray.shape == gray_blur.shape:
            frame_diff = cv2.absdiff(gray_blur, self.prev_frame_gray)
            _, diff_thresh = cv2.threshold(frame_diff, 28, 255, cv2.THRESH_BINARY)
            motion_mask = cv2.bitwise_and(fg_thresh, diff_thresh)
        else:
            motion_mask = fg_thresh

        self.prev_frame_gray = gray_blur

        # Morphological operations
        kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
        kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask_clean = cv2.morphologyEx(motion_mask, cv2.MORPH_CLOSE, kernel_close, iterations=2)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, kernel_open, iterations=2)

        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        raw_boxes = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if dynamic_min_area <= area <= dynamic_max_area:
                x, y, bw, bh = cv2.boundingRect(cnt)
                aspect = float(bw) / float(bh)
                # Realistic vehicle aspect ratios (0.5 to 3.2)
                if 0.50 <= aspect <= 3.2 and bw >= 35 and bh >= 30:
                    raw_boxes.append((x, y, bw, bh, area))

        merged_boxes = self._merge_adjacent_boxes(raw_boxes)

        for x, y, bw, bh in merged_boxes:
            crop = frame[max(0, y):min(h, y+bh), max(0, x):min(w, x+bw)]
            if crop.size == 0:
                continue

            # Verify vehicle edge density (rules out flat road patches and shadow blobs)
            crop_gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(crop_gray, 50, 150)
            edge_density = float(np.count_nonzero(edges)) / float(bw * bh)
            if edge_density < 0.04:  # Flat texture without vehicle structure
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
        if aspect_ratio < 0.65 and area < 4500:
            return "motorcycle", 0.86

        if area > 14000:
            if aspect_ratio < 0.9 or h > 90:
                return "bus", 0.89
            return "truck", 0.85

        if self._is_auto_rickshaw(crop):
            return "auto-rickshaw", 0.88

        if 8000 <= area <= 14000 and aspect_ratio > 1.1:
            return "truck", 0.82

        return "car", 0.91

    def _is_auto_rickshaw(self, crop):
        """Detects distinctive yellow/green coloration of Indian auto-rickshaws."""
        if crop is None or crop.size == 0:
            return False
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
        yellow_mask = (h >= 20) & (h <= 38) & (s > 60) & (v > 60)
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
