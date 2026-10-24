"""
Cross-Camera Re-Identification (Re-ID) Engine
Matches vehicle tracklets across non-overlapping cameras WITHOUT reading license plates.
Combines appearance feature similarity with spatio-temporal physics constraints.
"""

import math
from core.feature_extractor import compare_feature_signatures


class CrossCameraMatcher:
    def __init__(self, corridor_distance_meters=850.0, min_speed_kmh=15.0, max_speed_kmh=90.0):
        self.distance_meters = float(corridor_distance_meters)
        self.min_speed_kmh = float(min_speed_kmh)
        self.max_speed_kmh = float(max_speed_kmh)

        # Traffic engineering calculation:
        # Nominal speed is the mid-point of the corridor allowable speed envelope
        self.nominal_speed_kmh = (self.min_speed_kmh + self.max_speed_kmh) / 2.0  # e.g., 52.5 km/h
        self.min_transit_time_sec = self.distance_meters / (self.max_speed_kmh / 3.6)  # fastest (34.0s)
        self.max_transit_time_sec = self.distance_meters / (self.min_speed_kmh / 3.6)  # slowest (204.0s)
        self.expected_transit_time_sec = self.distance_meters / (self.nominal_speed_kmh / 3.6)  # nominal (~58.3s)

    def compute_spatio_temporal_score(self, exit_time_a, entry_time_b):
        """
        Evaluates physical travel time plausibility:
        delta_t = entry_time_b - exit_time_a
        Returns score in [0.0, 1.0] and estimated speed in km/h.
        """
        delta_t = entry_time_b - exit_time_a

        # Negative time means vehicle was seen in Cam B before Cam A
        if delta_t <= 0:
            return 0.0, 0.0, "Physical impossibility: Vehicle seen in downstream camera before upstream camera"

        speed_mps = self.distance_meters / delta_t
        speed_kmh = speed_mps * 3.6

        # Check if within realistic corridor speed limits
        if speed_kmh > (self.max_speed_kmh * 1.25):
            return 0.15, speed_kmh, f"Excessive speed ({speed_kmh:.1f} km/h) - exceeds corridor physical limit"
        elif speed_kmh < (self.min_speed_kmh * 0.6):
            return 0.25, speed_kmh, f"Prolonged transit ({delta_t:.1f}s) - vehicle likely stopped, turned, or parked"

        # Gaussian-like decay around realistic transit window
        deviation = abs(delta_t - self.expected_transit_time_sec)
        half_window = (self.max_transit_time_sec - self.min_transit_time_sec) / 2.0
        st_score = max(0.2, 1.0 - (deviation / half_window) * 0.6)

        return round(float(st_score), 3), round(float(speed_kmh), 1), f"Realistic corridor transit: {delta_t:.1f}s at {speed_kmh:.1f} km/h"

    def match_tracklets(self, cam_a_tracklets, cam_b_tracklets, confidence_threshold=0.55):
        """
        Calculates all candidate matches between Camera A exits and Camera B entries.
        cam_a_tracklets: list of VehicleTracklet
        cam_b_tracklets: list of VehicleTracklet
        """
        candidates = []
        match_counter = 1

        for track_a in cam_a_tracklets:
            if not track_a.features:
                continue

            for track_b in cam_b_tracklets:
                if not track_b.features:
                    continue

                # Spatio-temporal evaluation
                st_score, est_speed, st_note = self.compute_spatio_temporal_score(
                    track_a.last_timestamp,
                    track_b.first_timestamp
                )

                # Skip physically impossible chronological orders
                if st_score <= 0.0:
                    continue

                # Visual feature similarity
                vis_sim = compare_feature_signatures(track_a.features, track_b.features)

                # Overall confidence:
                # 60% visual appearance + 30% spatio-temporal physics + 10% type agreement
                type_bonus = 1.0 if track_a.features.get("vehicle_type") == track_b.features.get("vehicle_type") else 0.75
                overall_confidence = (0.60 * vis_sim + 0.30 * st_score + 0.10 * type_bonus)
                overall_confidence = round(float(overall_confidence), 3)

                transit_time = round(track_b.first_timestamp - track_a.last_timestamp, 1)

                # Formulate human-readable review explanation
                explanation_parts = []
                col_a = track_a.features.get("dominant_color_name", "Color")
                col_b = track_b.features.get("dominant_color_name", "Color")
                if col_a == col_b:
                    explanation_parts.append(f"Matching dominant color: {col_a}")
                else:
                    explanation_parts.append(f"Color tone variation: {col_a} (Cam A) vs {col_b} (Cam B)")

                type_a = track_a.features.get("vehicle_type", "Vehicle")
                type_b = track_b.features.get("vehicle_type", "Vehicle")
                if type_a == type_b:
                    explanation_parts.append(f"Consistent vehicle class: {type_a}")
                else:
                    explanation_parts.append(f"Class disparity: {type_a} vs {type_b}")

                explanation_parts.append(f"Transit: {transit_time}s across {self.distance_meters:.0f}m ({est_speed} km/h)")

                if overall_confidence >= confidence_threshold:
                    candidates.append({
                        "match_id": f"MATCH-{match_counter:03d}",
                        "cam_a_track_id": track_a.track_id,
                        "cam_b_track_id": track_b.track_id,
                        "cam_a_exit_time": round(track_a.last_timestamp, 1),
                        "cam_b_entry_time": round(track_b.first_timestamp, 1),
                        "transit_time_sec": transit_time,
                        "distance_meters": self.distance_meters,
                        "estimated_speed_kmh": est_speed,
                        "visual_similarity": vis_sim,
                        "spatio_temporal_score": st_score,
                        "overall_confidence": overall_confidence,
                        "vehicle_type_a": type_a,
                        "vehicle_type_b": type_b,
                        "color_a": col_a,
                        "color_b": col_b,
                        "hex_a": track_a.features.get("dominant_color_hex", "#666666"),
                        "hex_b": track_b.features.get("dominant_color_hex", "#666666"),
                        "aspect_ratio_a": track_a.features.get("aspect_ratio", 1.0),
                        "aspect_ratio_b": track_b.features.get("aspect_ratio", 1.0),
                        "explanation": "; ".join(explanation_parts),
                        "status": "pending",  # Operator review status: pending, accepted, rejected, flagged
                        "is_primary_candidate": False
                    })
                    match_counter += 1

        # Sort candidates descending by confidence
        candidates.sort(key=lambda x: x["overall_confidence"], reverse=True)

        # Flag 1-to-1 primary matches (greedy assignment so each Cam A and Cam B vehicle pair once as primary)
        assigned_a = set()
        assigned_b = set()
        for cand in candidates:
            a_id = cand["cam_a_track_id"]
            b_id = cand["cam_b_track_id"]
            if a_id not in assigned_a and b_id not in assigned_b:
                cand["is_primary_candidate"] = True
                assigned_a.add(a_id)
                assigned_b.add(b_id)

        return candidates
