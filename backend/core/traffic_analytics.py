"""
Traffic Analytics & Flow Estimation Module
Derives physical traffic parameters from cross-camera vehicle re-identification:
- Corridor transit times & speed distribution
- Bottleneck detection
- Vehicle composition split
"""

import numpy as np


def compute_corridor_analytics(matches, cam_a_total_count, cam_b_total_count, corridor_distance_meters=850.0):
    """
    matches: list of accepted/pending candidate matches
    cam_a_total_count: integer count of distinct vehicles seen at Cam A
    cam_b_total_count: integer count of distinct vehicles seen at Cam B
    """
    accepted_or_strong = [m for m in matches if m.get("status") in ["accepted", "pending"] and m.get("overall_confidence", 0) >= 0.55]

    if not accepted_or_strong:
        return {
            "corridor_distance_meters": corridor_distance_meters,
            "total_matches_detected": len(matches),
            "verified_matches": sum(1 for m in matches if m.get("status") == "accepted"),
            "rejected_matches": sum(1 for m in matches if m.get("status") == "rejected"),
            "match_rate_percent": 0.0,
            "avg_transit_time_sec": 0.0,
            "median_transit_time_sec": 0.0,
            "avg_speed_kmh": 0.0,
            "traffic_state": "Sparse / No Matches",
            "congestion_level": "Optimal",
            "vehicle_type_distribution": {},
            "color_distribution": {}
        }

    transit_times = [m["transit_time_sec"] for m in accepted_or_strong]
    speeds = [m["estimated_speed_kmh"] for m in accepted_or_strong]

    avg_transit = float(np.mean(transit_times))
    median_transit = float(np.median(transit_times))
    avg_speed = float(np.mean(speeds))

    # Match rate: percentage of unique Cam A vehicles that reached Cam B
    # Count unique Cam A vehicles that have a primary or verified match
    matched_cam_a_ids = set(
        m["cam_a_track_id"] for m in accepted_or_strong
        if m.get("is_primary_candidate") or m.get("status") == "accepted"
    )
    match_rate = min(100.0, (len(matched_cam_a_ids) / max(1, cam_a_total_count)) * 100.0)

    # Traffic congestion diagnosis based on speed
    if avg_speed >= 45.0:
        congestion_level = "Free Flow"
        traffic_state = "Normal uncongested progression"
    elif 25.0 <= avg_speed < 45.0:
        congestion_level = "Moderate Density"
        traffic_state = "Sub-optimal speeds; minor junction queueing"
    else:
        congestion_level = "Congested / Bottleneck"
        traffic_state = "Severe delay detected between sensors"

    # Vehicle type breakdown
    type_counts = {}
    color_counts = {}
    for m in accepted_or_strong:
        v_type = m.get("vehicle_type_a", "Other")
        type_counts[v_type] = type_counts.get(v_type, 0) + 1
        col = m.get("color_a", "Other")
        color_counts[col] = color_counts.get(col, 0) + 1

    return {
        "corridor_distance_meters": corridor_distance_meters,
        "total_matches_detected": len(matches),
        "verified_matches": sum(1 for m in matches if m.get("status") == "accepted"),
        "rejected_matches": sum(1 for m in matches if m.get("status") == "rejected"),
        "match_rate_percent": round(match_rate, 1),
        "avg_transit_time_sec": round(avg_transit, 1),
        "median_transit_time_sec": round(median_transit, 1),
        "avg_speed_kmh": round(avg_speed, 1),
        "traffic_state": traffic_state,
        "congestion_level": congestion_level,
        "vehicle_type_distribution": type_counts,
        "color_distribution": color_counts
    }
