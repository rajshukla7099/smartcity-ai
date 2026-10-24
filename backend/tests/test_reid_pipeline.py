"""
Automated Test Suite for CityTrack AI
Validates core computer vision algorithms, Re-ID matcher, and Flask API endpoints.
"""

import unittest
import numpy as np
import cv2
import io
import sys
import os

# Ensure backend directory is in sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from core.feature_extractor import (
    extract_vehicle_features,
    compare_feature_signatures,
    get_dominant_color,
    estimate_vehicle_type
)
from core.tracker import (
    compute_iou,
    VehicleTracklet,
    SingleCameraTracker
)
from core.reid_matcher import CrossCameraMatcher
from core.traffic_analytics import compute_corridor_analytics
from app import app


class TestFeatureExtractor(unittest.TestCase):
    def setUp(self):
        # Create a synthetic 100x60 BGR vehicle crop (Red vehicle with dark roof)
        self.crop = np.zeros((100, 60, 3), dtype=np.uint8)
        self.crop[0:30, :] = (40, 40, 40)       # Dark roof
        self.crop[30:75, :] = (30, 30, 210)     # Crimson red body
        self.crop[75:100, :] = (20, 20, 20)     # Dark chassis / wheels

    def test_extract_features_structure(self):
        feat = extract_vehicle_features(self.crop)
        self.assertIsNotNone(feat)
        self.assertIn("aspect_ratio", feat)
        self.assertIn("dominant_color_name", feat)
        self.assertIn("dominant_color_hex", feat)
        self.assertIn("hist_top", feat)
        self.assertIn("hist_mid", feat)
        self.assertIn("hist_bot", feat)
        self.assertIn("vehicle_type", feat)
        self.assertAlmostEqual(feat["aspect_ratio"], 0.6, delta=0.05)

    def test_dominant_color_detection(self):
        hex_code, color_name = get_dominant_color(self.crop)
        self.assertTrue(hex_code.startswith("#"))
        self.assertIn("Red", color_name)

    def test_compare_identical_signatures(self):
        feat = extract_vehicle_features(self.crop)
        score = compare_feature_signatures(feat, feat)
        self.assertGreater(score, 0.95)

    def test_compare_contrasting_signatures(self):
        # Create a contrasting vehicle (Blue truck: different dimensions and different color)
        blue_truck = np.full((120, 100, 3), (180, 50, 20), dtype=np.uint8)
        feat_red = extract_vehicle_features(self.crop)
        feat_blue = extract_vehicle_features(blue_truck)
        score = compare_feature_signatures(feat_red, feat_blue)
        self.assertLess(score, 0.65)


class TestTrackerAndIoU(unittest.TestCase):
    def test_iou_identical_boxes(self):
        box = (10, 20, 50, 60)
        self.assertAlmostEqual(compute_iou(box, box), 1.0)

    def test_iou_disjoint_boxes(self):
        box1 = (0, 0, 10, 10)
        box2 = (50, 50, 10, 10)
        self.assertEqual(compute_iou(box1, box2), 0.0)

    def test_single_camera_tracker_association(self):
        tracker = SingleCameraTracker(camera_id="CAM-A", iou_threshold=0.3)
        # Frame 0: Vehicle at (100, 100, 40, 60)
        det0 = [{"bbox": (100, 100, 40, 60), "crop": np.zeros((60, 40, 3), dtype=np.uint8), "features": {}}]
        tracker.process_frame_detections(det0, frame_idx=0, timestamp_sec=0.0)
        self.assertEqual(len(tracker.active_tracks), 1)
        initial_id = tracker.active_tracks[0].track_id

        # Frame 1: Vehicle shifted slightly down to (100, 108, 40, 60)
        det1 = [{"bbox": (100, 108, 40, 60), "crop": np.zeros((60, 40, 3), dtype=np.uint8), "features": {}}]
        tracker.process_frame_detections(det1, frame_idx=1, timestamp_sec=0.033)
        self.assertEqual(len(tracker.active_tracks), 1)
        self.assertEqual(tracker.active_tracks[0].track_id, initial_id)


class TestReIDMatcherAndPhysics(unittest.TestCase):
    def setUp(self):
        self.matcher = CrossCameraMatcher(corridor_distance_meters=850.0, min_speed_kmh=15.0, max_speed_kmh=90.0)

    def test_spatio_temporal_chronological_violation(self):
        # Entry in Cam B happened BEFORE exit in Cam A (impossible)
        score, speed, note = self.matcher.compute_spatio_temporal_score(exit_time_a=50.0, entry_time_b=40.0)
        self.assertEqual(score, 0.0)
        self.assertEqual(speed, 0.0)

    def test_spatio_temporal_plausible_transit(self):
        # 850m traveled in 55.0s -> 55.6 km/h (typical urban corridor speed)
        score, speed, note = self.matcher.compute_spatio_temporal_score(exit_time_a=10.0, entry_time_b=65.0)
        self.assertGreater(score, 0.70)
        self.assertAlmostEqual(speed, 55.6, delta=1.0)


class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_status_endpoint(self):
        res = self.client.get("/api/status")
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data["status"], "online")
        self.assertIn("corridor_distance_meters", data)

    def test_demo_dataset_endpoint(self):
        res = self.client.get("/api/dataset/demo")
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertTrue(data["is_demo"])
        self.assertIn("camera_a", data)
        self.assertIn("camera_b", data)
        self.assertIn("matches", data)
        self.assertIn("analytics", data)
        self.assertGreater(len(data["matches"]), 0)

    def test_match_review_action(self):
        # Get first match
        demo_res = self.client.get("/api/dataset/demo")
        first_match = demo_res.json["matches"][0]
        m_id = first_match["match_id"]

        # Accept match
        review_res = self.client.post(
            f"/api/matches/{m_id}/review",
            json={"action": "accepted", "notes": "Verified by reviewer"}
        )
        self.assertEqual(review_res.status_code, 200)
        self.assertEqual(review_res.json["new_status"], "accepted")

        # Reject match
        review_res_rej = self.client.post(
            f"/api/matches/{m_id}/review",
            json={"action": "rejected", "notes": "Incorrect distractor"}
        )
        self.assertEqual(review_res_rej.status_code, 200)
        self.assertEqual(review_res_rej.json["new_status"], "rejected")

    def test_corridor_configure_endpoint(self):
        res = self.client.post(
            "/api/corridor/configure",
            json={"corridor_distance_meters": 1200.0, "confidence_threshold": 0.60}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data["parameters"]["corridor_distance_meters"], 1200.0)

    def test_methodology_endpoint(self):
        res = self.client.get("/api/methodology")
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertIn("pipeline_stages", data)
        self.assertIn("limitations", data)
        self.assertEqual(len(data["pipeline_stages"]), 6)
        self.assertEqual(len(data["limitations"]), 4)

    def test_upload_analysis_flow(self):
        # Generate two synthetic test images in-memory
        img_a = np.zeros((360, 640, 3), dtype=np.uint8)
        img_a[100:180, 150:230] = (200, 50, 50)  # Red box simulating vehicle

        img_b = np.zeros((360, 640, 3), dtype=np.uint8)
        img_b[100:180, 150:230] = (195, 48, 52)  # Slightly shifted red box

        _, buf_a = cv2.imencode(".jpg", img_a)
        _, buf_b = cv2.imencode(".jpg", img_b)

        data = {
            "camera_a": (io.BytesIO(buf_a.tobytes()), "cam_a.jpg"),
            "camera_b": (io.BytesIO(buf_b.tobytes()), "cam_b.jpg")
        }

        res = self.client.post(
            "/api/analyze/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json["success"])
        self.assertFalse(res.json["is_demo"])

    def test_frontend_static_serving(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"CityTrack AI", res.data)

    def test_model_architecture_endpoint(self):
        res = self.client.get("/api/model/architecture")
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertIn("backbone", data)
        self.assertIn("spatial_partitioning", data)
        self.assertIn("embedding_head", data)
        self.assertEqual(data["embedding_head"]["dimension"], 64)

    def test_model_embeddings_endpoint(self):
        res = self.client.get("/api/model/embeddings")
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertIn("similarity_matrix", data)
        self.assertIn("vehicles_a", data)
        self.assertIn("vehicles_b", data)

    def test_model_probe_endpoint(self):
        res = self.client.post("/api/model/probe", json={"probe_id": "CAM-A-V-01"})
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data["probe_id"], "CAM-A-V-01")

    def test_traffic_od_flow_endpoint(self):
        res = self.client.get("/api/traffic/od-matrix")
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertIn("modal_split_counts", data)
        self.assertIn("hourly_flow_rate_vph", data)

    def test_camera_stream_endpoint(self):
        res = self.client.get("/api/stream/cam_a")
        self.assertEqual(res.status_code, 200)
        self.assertIn("multipart/x-mixed-replace", res.content_type)


if __name__ == "__main__":
    unittest.main()
