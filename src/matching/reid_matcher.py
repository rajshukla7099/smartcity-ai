"""
MultiCam AI - Cross-Camera Vehicle Re-Identification Engine
Matches vehicle tracklets across non-overlapping surveillance cameras using:
1. Spatio-temporal travel-time physics window: Δt = tB - tA ∈ [d/v_max, d/v_min]
2. Visual appearance cosine similarity (3-stripe HSV & 64d latent embeddings)
3. Vehicle class compatibility
4. 1-to-1 Bipartite matching with human-in-the-loop review state.
"""

import math
from src.features.appearance import compute_visual_similarity

class CrossCameraMatch:
    def __init__(self, match_id, track_a, track_b, corridor_distance=850.0):
        self.match_id = match_id
        self.track_a = track_a
        self.track_b = track_b
        self.corridor_distance = corridor_distance

        # Timestamps
        self.t_a = track_a.exit_time
        self.t_b = track_b.entry_time
        self.delta_t = max(0.01, self.t_b - self.t_a)

        # Physics velocity
        self.speed_kmh = round((self.corridor_distance / self.delta_t) * 3.6, 1)

        # Visual appearance score
        self.vis_similarity = compute_visual_similarity(track_a.features, track_b.features)

        # Spatio-temporal score
        self.st_score = 0.0

        # Class match score
        self.type_score = 1.0 if track_a.class_name == track_b.class_name else 0.40

        # Overall confidence
        self.confidence = 0.0

        # Review status: 'verified', 'rejected', 'pending'
        self.status = "pending"
        self.is_primary = False

    def to_dict(self):
        feat_a = self.track_a.features or {}
        feat_b = self.track_b.features or {}
        return {
            "match_id": self.match_id,
            "track_id_a": self.track_a.track_id,
            "track_id_b": self.track_b.track_id,
            "camera_a": self.track_a.camera_id,
            "camera_b": self.track_b.camera_id,
            "class_a": self.track_a.class_name,
            "class_b": self.track_b.class_name,
            "name_a": feat_a.get("vehicle_name", self.track_a.class_name.upper()),
            "name_b": feat_b.get("vehicle_name", self.track_b.class_name.upper()),
            "make_a": feat_a.get("vehicle_make", "Unknown"),
            "make_b": feat_b.get("vehicle_make", "Unknown"),
            "model_a": feat_a.get("vehicle_model", "Unknown"),
            "model_b": feat_b.get("vehicle_model", "Unknown"),
            "body_a": feat_a.get("body_type", "Standard"),
            "body_b": feat_b.get("body_type", "Standard"),
            "color_a": feat_a.get("dominant_color", "Unknown"),
            "color_b": feat_b.get("dominant_color", "Unknown"),
            "hex_a": feat_a.get("dominant_hex", "#777777"),
            "hex_b": feat_b.get("dominant_hex", "#777777"),
            "t_a": round(self.t_a, 2),
            "t_b": round(self.t_b, 2),
            "delta_t": round(self.delta_t, 2),
            "speed_kmh": self.speed_kmh,
            "visual_similarity": round(self.vis_similarity, 3),
            "spatio_temporal_score": round(self.st_score, 3),
            "overall_confidence": round(self.confidence, 3),
            "status": self.status,
            "is_primary": self.is_primary
        }


class CrossCameraReIDMatcher:
    """
    Solves cross-camera association across non-overlapping corridor cameras.
    """
    def __init__(self, corridor_distance=850.0, min_speed_kmh=15.0, max_speed_kmh=95.0, confidence_threshold=0.55):
        self.corridor_distance = corridor_distance
        self.min_speed_kmh = min_speed_kmh
        self.max_speed_kmh = max_speed_kmh
        self.confidence_threshold = confidence_threshold

        # Min and Max travel times in seconds
        self.min_travel_time = self.corridor_distance / (self.max_speed_kmh / 3.6)
        self.max_travel_time = self.corridor_distance / (self.min_speed_kmh / 3.6)
        self.nominal_travel_time = (self.min_travel_time + self.max_travel_time) / 2.0

    def compute_spatio_temporal_score(self, delta_t):
        """Gaussian proximity around expected transit speed envelope."""
        if delta_t <= 0:
            return 0.001

        # Check bounds
        if delta_t < self.min_travel_time * 0.8:
            # Physically impossible overspeeding
            return 0.10
        if delta_t > self.max_travel_time * 1.5:
            # Too slow / likely diverted into side street
            return 0.15

        # Gaussian decay around nominal travel time
        sigma = (self.max_travel_time - self.min_travel_time) / 2.5
        score = math.exp(-0.5 * ((delta_t - self.nominal_travel_time) / sigma) ** 2)
        return max(0.05, min(1.0, score))

    def match_cameras(self, tracks_a, tracks_b):
        """
        Computes pairwise cross-camera compatibility matrix, runs 1-to-1 bipartite assignment.
        tracks_a: list of VehicleTrack from Camera A
        tracks_b: list of VehicleTrack from Camera B
        """
        all_candidates = []
        match_counter = 1

        for trk_a in tracks_a:
            for trk_b in tracks_b:
                match = CrossCameraMatch(
                    match_id=f"REID-{match_counter:03d}",
                    track_a=trk_a,
                    track_b=trk_b,
                    corridor_distance=self.corridor_distance
                )
                match_counter += 1

                # Calculate spatio-temporal score
                match.st_score = self.compute_spatio_temporal_score(match.delta_t)

                # Combined multi-modal score:
                # 50% Visual Appearance, 35% Spatio-Temporal Travel Time, 15% Vehicle Type Match
                combined = (
                    0.50 * match.vis_similarity +
                    0.35 * match.st_score +
                    0.15 * match.type_score
                )
                match.confidence = combined

                if combined >= self.confidence_threshold:
                    all_candidates.append(match)

        # Sort candidate matches by confidence descending
        all_candidates.sort(key=lambda m: m.confidence, reverse=True)

        # 1-to-1 Bipartite Greedy Assignment
        assigned_a = set()
        assigned_b = set()

        for m in all_candidates:
            id_a = m.track_a.track_id
            id_b = m.track_b.track_id
            if id_a not in assigned_a and id_b not in assigned_b:
                m.is_primary = True
                m.status = "verified"
                assigned_a.add(id_a)
                assigned_b.add(id_b)
            else:
                m.is_primary = False
                m.status = "pending"

        return all_candidates
