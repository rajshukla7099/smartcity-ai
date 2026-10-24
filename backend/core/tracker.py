"""
Intra-Camera Vehicle Tracker Module
Maintains tracklets within a single camera feed across time frames.
Uses IoU and centroid association to maintain persistent track IDs
and capture best-quality crops for downstream cross-camera Re-ID.
"""

import math
import numpy as np


class VehicleTracklet:
    """Represents a continuous tracklet of a single vehicle in one camera."""
    def __init__(self, track_id, camera_id, initial_bbox, frame_idx, timestamp_sec, crop_img, features):
        self.track_id = track_id
        self.camera_id = camera_id
        self.bboxes = [initial_bbox]
        self.first_frame = frame_idx
        self.last_frame = frame_idx
        self.first_timestamp = timestamp_sec
        self.last_timestamp = timestamp_sec
        self.best_crop = crop_img
        self.best_crop_area = initial_bbox[2] * initial_bbox[3]
        self.features = features
        self.trajectory = [self._centroid(initial_bbox)]
        self.missed_frames = 0
        self.is_completed = False

    def _centroid(self, bbox):
        x, y, w, h = bbox
        return (x + w / 2.0, y + h / 2.0)

    def update(self, bbox, frame_idx, timestamp_sec, crop_img, features):
        self.bboxes.append(bbox)
        self.last_frame = frame_idx
        self.last_timestamp = timestamp_sec
        self.trajectory.append(self._centroid(bbox))
        self.missed_frames = 0

        # Retain highest resolution crop
        area = bbox[2] * bbox[3]
        if area > self.best_crop_area and crop_img is not None:
            self.best_crop = crop_img
            self.best_crop_area = area
            if features is not None:
                self.features = features

    def get_direction(self):
        """Estimates movement vector (vertical flow or horizontal flow)."""
        if len(self.trajectory) < 2:
            return "Stationary / Ingress"
        start_y = self.trajectory[0][1]
        end_y = self.trajectory[-1][1]
        dy = end_y - start_y
        if dy > 15:
            return "Downstream Corridor"
        elif dy < -15:
            return "Upstream Corridor"
        return "Steady Transition"

    def to_dict(self):
        return {
            "track_id": self.track_id,
            "camera_id": self.camera_id,
            "first_frame": self.first_frame,
            "last_frame": self.last_frame,
            "entry_time": round(self.first_timestamp, 2),
            "exit_time": round(self.last_timestamp, 2),
            "duration_sec": round(self.last_timestamp - self.first_timestamp, 2),
            "direction": self.get_direction(),
            "vehicle_type": self.features.get("vehicle_type", "Unknown") if self.features else "Unknown",
            "dominant_color": self.features.get("dominant_color_name", "Unknown") if self.features else "Unknown",
            "dominant_hex": self.features.get("dominant_color_hex", "#777777") if self.features else "#777777",
            "aspect_ratio": self.features.get("aspect_ratio", 1.0) if self.features else 1.0
        }


def compute_iou(box_a, box_b):
    """Computes Intersection over Union between two bounding boxes (x, y, w, h)."""
    xA = max(box_a[0], box_b[0])
    yA = max(box_a[1], box_b[1])
    xB = min(box_a[0] + box_a[2], box_b[0] + box_b[2])
    yB = min(box_a[1] + box_a[3], box_b[1] + box_b[3])

    inter_w = max(0, xB - xA)
    inter_h = max(0, yB - yA)
    inter_area = inter_w * inter_h

    box_a_area = box_a[2] * box_a[3]
    box_b_area = box_b[2] * box_b[3]
    union_area = float(box_a_area + box_b_area - inter_area)
    if union_area <= 0:
        return 0.0
    return inter_area / union_area


class SingleCameraTracker:
    """Associates detections across frames within a single camera."""
    def __init__(self, camera_id="CAM-A", max_missed_frames=8, iou_threshold=0.25):
        self.camera_id = camera_id
        self.max_missed_frames = max_missed_frames
        self.iou_threshold = iou_threshold
        self.next_track_id = 1
        self.active_tracks = []
        self.completed_tracks = []

    def process_frame_detections(self, detections, frame_idx, timestamp_sec):
        """
        detections: list of dicts with keys:
          'bbox': (x, y, w, h)
          'crop': numpy array
          'features': feature dict
        """
        unmatched_detections = list(range(len(detections)))
        matched_tracks = set()

        # Step 1: Greedy match based on IoU
        for t_idx, track in enumerate(self.active_tracks):
            last_box = track.bboxes[-1]
            best_iou = 0.0
            best_det_idx = None

            for d_idx in unmatched_detections:
                iou = compute_iou(last_box, detections[d_idx]["bbox"])
                if iou > best_iou:
                    best_iou = iou
                    best_det_idx = d_idx

            if best_iou >= self.iou_threshold and best_det_idx is not None:
                det = detections[best_det_idx]
                track.update(
                    det["bbox"],
                    frame_idx,
                    timestamp_sec,
                    det.get("crop"),
                    det.get("features")
                )
                matched_tracks.add(t_idx)
                unmatched_detections.remove(best_det_idx)

        # Step 2: Handle unmatched active tracks (increment missed count)
        for t_idx, track in enumerate(self.active_tracks):
            if t_idx not in matched_tracks:
                track.missed_frames += 1

        # Step 3: Archive tracks that have exited the camera field of view
        surviving_tracks = []
        for track in self.active_tracks:
            if track.missed_frames > self.max_missed_frames:
                track.is_completed = True
                self.completed_tracks.append(track)
            else:
                surviving_tracks.append(track)
        self.active_tracks = surviving_tracks

        # Step 4: Initiate new tracks for new detections
        for d_idx in unmatched_detections:
            det = detections[d_idx]
            new_id = f"{self.camera_id}-{self.next_track_id:03d}"
            self.next_track_id += 1
            new_track = VehicleTracklet(
                track_id=new_id,
                camera_id=self.camera_id,
                initial_bbox=det["bbox"],
                frame_idx=frame_idx,
                timestamp_sec=timestamp_sec,
                crop_img=det.get("crop"),
                features=det.get("features")
            )
            self.active_tracks.append(new_track)

    def finalize(self):
        """Marks all active tracks as completed at end of video/stream."""
        for track in self.active_tracks:
            track.is_completed = True
            self.completed_tracks.append(track)
        self.active_tracks = []
        return self.completed_tracks
