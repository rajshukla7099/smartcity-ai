"""
MultiCam AI - Multi-Object Tracker (ByteTrack / IoU Association)
Assigns temporary track IDs to vehicles within each camera view,
records ingress/egress timestamps, and retains the clearest vehicle crop.
"""

import numpy as np

def compute_iou(box_a, box_b):
    """Computes Intersection over Union between two boxes (x, y, w, h)."""
    ax, ay, aw, ah = box_a
    bx, by, bw, bh = box_b

    x1 = max(ax, bx)
    y1 = max(ay, by)
    x2 = min(ax + aw, bx + bw)
    y2 = min(ay + ah, by + bh)

    inter_w = max(0, x2 - x1)
    inter_h = max(0, y2 - y1)
    inter_area = inter_w * inter_h

    area_a = aw * ah
    area_b = bw * bh
    union_area = area_a + area_b - inter_area

    if union_area <= 0:
        return 0.0
    return float(inter_area) / float(union_area)


def compute_tracking_affinity(box_det, last_box, predicted_box):
    """
    Computes robust tracking association score combining IoU, motion prediction,
    and centroid distance. Handles fast-moving vehicles even when frames are sampled.
    """
    iou_last = compute_iou(box_det, last_box)
    iou_pred = compute_iou(box_det, predicted_box)
    base_iou = max(iou_last, iou_pred)
    if base_iou > 0.05:
        return base_iou

    # Centroid distance fallback when bounding boxes don't intersect due to vehicle speed
    dx, dy, dw, dh = box_det
    px, py, pw, ph = predicted_box

    c_det_x, c_det_y = dx + dw / 2.0, dy + dh / 2.0
    c_pred_x, c_pred_y = px + pw / 2.0, py + ph / 2.0

    dist = np.hypot(c_det_x - c_pred_x, c_det_y - c_pred_y)
    ref_scale = np.hypot(max(dw, pw), max(dh, ph))
    if ref_scale <= 0:
        return 0.0

    norm_dist = dist / ref_scale
    if norm_dist < 1.75:
        # Give proximity score between 0.12 and 0.45
        return float(max(0.12, 0.45 * (1.0 - norm_dist / 1.75)))
    return 0.0


class VehicleTrack:
    """Tracks a single vehicle across continuous frames inside one camera."""
    def __init__(self, track_id, camera_id, initial_bbox, class_name, confidence, crop, timestamp):
        self.track_id = track_id
        self.camera_id = camera_id
        self.bboxes = [initial_bbox]
        self.class_name = class_name
        self.confidence = confidence
        self.best_crop = crop
        self.entry_time = timestamp
        self.exit_time = timestamp
        self.missed_frames = 0
        self.is_active = True
        self.features = None  # To be filled by AppearanceFeatureExtractor
        self.vx = 0.0
        self.vy = 0.0

    def predict_bbox(self):
        """Predicts vehicle position based on momentum/velocity vector."""
        lx, ly, lw, lh = self.bboxes[-1]
        return (lx + self.vx, ly + self.vy, lw, lh)

    def update(self, bbox, confidence, crop, timestamp):
        lx, ly, _, _ = self.bboxes[-1]
        cx, cy, _, _ = bbox

        # Smooth velocity filter (Kalman-like momentum smoothing)
        self.vx = 0.65 * self.vx + 0.35 * (cx - lx)
        self.vy = 0.65 * self.vy + 0.35 * (cy - ly)

        self.bboxes.append(bbox)
        self.confidence = 0.8 * self.confidence + 0.2 * confidence
        self.exit_time = timestamp
        self.missed_frames = 0

        # Replace crop if new crop has higher resolution or sharper details
        if crop is not None and crop.size > 0:
            if self.best_crop is None or crop.size > self.best_crop.size:
                self.best_crop = crop

    def mark_missed(self):
        self.missed_frames += 1

    def to_dict(self):
        return {
            "track_id": self.track_id,
            "camera_id": self.camera_id,
            "class_name": self.class_name,
            "confidence": round(self.confidence, 3),
            "entry_time": round(self.entry_time, 2),
            "exit_time": round(self.exit_time, 2),
            "duration_sec": round(self.exit_time - self.entry_time, 2),
            "last_bbox": self.bboxes[-1] if self.bboxes else None,
            "num_observations": len(self.bboxes)
        }


class MultiObjectTracker:
    """Associates detections into persistent vehicle tracklets within a camera."""
    def __init__(self, camera_id="CAM-A", iou_threshold=0.15, max_missed_frames=15):
        self.camera_id = camera_id
        self.iou_threshold = iou_threshold
        self.max_missed_frames = max_missed_frames
        self.tracks = []
        self.next_id = 1

    def update(self, detections, timestamp):
        """
        Updates tracks with detections for the current frame.
        detections: list of VehicleDetection
        """
        active_tracks = [t for t in self.tracks if t.is_active]

        if not active_tracks:
            # All detections start new tracks
            for det in detections:
                tid = f"{self.camera_id}-TRK-{self.next_id:03d}"
                self.next_id += 1
                t = VehicleTrack(tid, self.camera_id, det.bbox, det.class_name, det.confidence, det.crop, timestamp)
                self.tracks.append(t)
            return self.get_active_tracks()

        # Build affinity matrix combining IoU, motion prediction and centroid distance
        matched_track_indices = set()
        matched_det_indices = set()

        for d_idx, det in enumerate(detections):
            best_score = 0.0
            best_t_idx = -1
            for t_idx, trk in enumerate(active_tracks):
                if t_idx in matched_track_indices:
                    continue
                # Class compatibility bonus
                class_bonus = 0.06 if det.class_name == trk.class_name else 0.0
                score = compute_tracking_affinity(det.bbox, trk.bboxes[-1], trk.predict_bbox()) + class_bonus
                if score > best_score:
                    best_score = score
                    best_t_idx = t_idx

            if best_score >= self.iou_threshold and best_t_idx >= 0:
                active_tracks[best_t_idx].update(det.bbox, det.confidence, det.crop, timestamp)
                matched_track_indices.add(best_t_idx)
                matched_det_indices.add(d_idx)

        # Mark unmatched active tracks as missed
        for t_idx, trk in enumerate(active_tracks):
            if t_idx not in matched_track_indices:
                trk.mark_missed()
                if trk.missed_frames > self.max_missed_frames:
                    trk.is_active = False

        # Create new tracks for unmatched detections
        for d_idx, det in enumerate(detections):
            if d_idx not in matched_det_indices:
                tid = f"{self.camera_id}-TRK-{self.next_id:03d}"
                self.next_id += 1
                t = VehicleTrack(tid, self.camera_id, det.bbox, det.class_name, det.confidence, det.crop, timestamp)
                self.tracks.append(t)

        return self.get_active_tracks()

    def get_active_tracks(self):
        return [t for t in self.tracks if t.is_active]

    def get_all_completed_tracks(self):
        return self.tracks
