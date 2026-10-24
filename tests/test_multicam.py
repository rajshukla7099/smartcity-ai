"""
MultiCam AI - Comprehensive Test Suite
Verifies:
1. Vehicle detection & classification
2. Multi-object tracking (tracklet generation)
3. Appearance feature extraction (no OCR)
4. Cross-camera Re-ID bipartite matching with physics gating
5. Traffic flow O-D matrix analytics
6. Camera failure simulation
7. Privacy-safe k-anonymity aggregation export
"""

import unittest
import numpy as np
import cv2

from src.detection.detector import HybridVehicleDetector, VehicleDetection
from src.tracking.tracker import MultiObjectTracker, compute_iou
from src.features.appearance import AppearanceFeatureExtractor, compute_visual_similarity
from src.features.make_model_classifier import VehicleMakeModelClassifier
from src.matching.reid_matcher import CrossCameraReIDMatcher
from src.analytics.traffic_analytics import TrafficAnalyticsEngine
from src.privacy.privacy_guard import PrivacySafeExporter

class TestMultiCamAI(unittest.TestCase):
    def setUp(self):
        self.detector = HybridVehicleDetector()
        self.tracker_a = MultiObjectTracker(camera_id="CAM-A")
        self.tracker_b = MultiObjectTracker(camera_id="CAM-B")
        self.extractor = AppearanceFeatureExtractor()
        self.matcher = CrossCameraReIDMatcher(corridor_distance=850.0)
        self.analytics = TrafficAnalyticsEngine(corridor_distance=850.0)
        self.privacy = PrivacySafeExporter(min_k=10)

    def test_iou_computation(self):
        box1 = (10, 10, 50, 50)
        box2 = (10, 10, 50, 50)
        self.assertAlmostEqual(compute_iou(box1, box2), 1.0)

        box3 = (100, 100, 50, 50)
        self.assertEqual(compute_iou(box1, box3), 0.0)

    def test_appearance_feature_extraction(self):
        # Create a synthetic yellow car crop (e.g. auto-rickshaw or taxi)
        img = np.full((100, 80, 3), (30, 200, 230), dtype=np.uint8)
        feat = self.extractor.extract(img)

        self.assertIn("dominant_color", feat)
        self.assertIn("dominant_hex", feat)
        self.assertEqual(len(feat["embedding_64d"]), 64)
        # Check L2 normalization
        norm = np.linalg.norm(feat["embedding_64d"])
        self.assertAlmostEqual(norm, 1.0, places=3)

    def test_visual_similarity(self):
        img_a = np.full((100, 80, 3), (40, 140, 220), dtype=np.uint8)
        img_b = np.full((100, 80, 3), (42, 142, 218), dtype=np.uint8)
        img_c = np.full((100, 80, 3), (20, 20, 20), dtype=np.uint8)

        feat_a = self.extractor.extract(img_a)
        feat_b = self.extractor.extract(img_b)
        feat_c = self.extractor.extract(img_c)

        sim_same = compute_visual_similarity(feat_a, feat_b)
        sim_diff = compute_visual_similarity(feat_a, feat_c)

        self.assertGreater(sim_same, sim_diff)

    def test_cross_camera_matching_and_physics_gating(self):
        # Vehicle 1 in Cam A: Exit at t=10s
        crop_a = np.full((80, 60, 3), (40, 140, 220), dtype=np.uint8)
        det_a = [VehicleDetection((50, 50, 60, 80), "car", 0.9, crop_a)]
        self.tracker_a.update(det_a, timestamp=10.0)
        tracks_a = self.tracker_a.get_all_completed_tracks()
        tracks_a[0].features = self.extractor.extract(crop_a)

        # Vehicle 1 in Cam B: Entry at t=65s (travel time 55s -> ~55 km/h)
        crop_b = np.full((80, 60, 3), (42, 142, 218), dtype=np.uint8)
        det_b = [VehicleDetection((60, 60, 60, 80), "car", 0.88, crop_b)]
        self.tracker_b.update(det_b, timestamp=65.0)
        tracks_b = self.tracker_b.get_all_completed_tracks()
        tracks_b[0].features = self.extractor.extract(crop_b)

        matches = self.matcher.match_cameras(tracks_a, tracks_b)
        self.assertGreaterEqual(len(matches), 1)
        self.assertTrue(matches[0].is_primary)
        self.assertEqual(matches[0].status, "verified")
        self.assertAlmostEqual(matches[0].delta_t, 55.0, places=1)

    def test_traffic_analytics_and_failure_sim(self):
        crop = np.full((80, 60, 3), (30, 200, 230), dtype=np.uint8)
        det = [VehicleDetection((50, 50, 60, 80), "auto-rickshaw", 0.9, crop)]
        self.tracker_a.update(det, timestamp=10.0)
        tracks_a = self.tracker_a.get_all_completed_tracks()
        tracks_a[0].features = self.extractor.extract(crop)

        verified = [{
            "delta_t": 55.0,
            "speed_kmh": 55.6,
            "track_id_a": tracks_a[0].track_id,
            "track_id_b": "CAM-B-TRK-001"
        }]

        analytics_out = self.analytics.compute_corridor_analytics(tracks_a, tracks_a, verified)
        self.assertIn("flow_rate_vph", analytics_out)
        self.assertIn("od_matrix", analytics_out)

        # Failure simulation
        failure_res = self.analytics.simulate_camera_failure(tracks_a, tracks_a, failed_camera="Camera B")
        self.assertIn("estimated_corridor_flow_vph", failure_res)
        self.assertIn("estimation_error_pct", failure_res)

    def test_privacy_safe_k_anonymity(self):
        crop = np.full((80, 60, 3), (30, 200, 230), dtype=np.uint8)
        det = [VehicleDetection((50, 50, 60, 80), "car", 0.9, crop)]
        self.tracker_a.update(det, timestamp=10.0)
        tracks_a = self.tracker_a.get_all_completed_tracks()
        analytics_out = self.analytics.compute_corridor_analytics(tracks_a, tracks_a, [])

        report = self.privacy.generate_privacy_report(analytics_out)
        self.assertFalse(report.empty)
        # Check no persistent individual track IDs leak into privacy export
        csv_str = self.privacy.export_csv_string(report)
        self.assertNotIn("TRK-", csv_str)
        self.assertIn("License Plate OCR Exemption", csv_str)


    def test_night_metrics_and_idf1(self):
        # Night Metrics: IDF1 & Night flow error
        crop = np.full((80, 60, 3), (30, 200, 230), dtype=np.uint8)
        det = [VehicleDetection((50, 50, 60, 80), "car", 0.9, crop)]
        self.tracker_a.update(det, timestamp=10.0)
        tracks_a = self.tracker_a.get_all_completed_tracks()

        verified = [{"track_id_a": tracks_a[0].track_id, "track_id_b": "CAM-B-TRK-001"}]
        night_metrics_clahe = self.analytics.compute_night_metrics(tracks_a, tracks_a, verified, with_clahe=True)
        night_metrics_raw = self.analytics.compute_night_metrics(tracks_a, tracks_a, verified, with_clahe=False)

        self.assertIn("idf1_score", night_metrics_clahe)
        self.assertIn("night_flow_error_pct", night_metrics_clahe)
        self.assertGreater(night_metrics_clahe["idf1_score"], night_metrics_raw["idf1_score"])
        self.assertLess(night_metrics_clahe["night_flow_error_pct"], night_metrics_raw["night_flow_error_pct"])

    def test_unseen_camera_zero_shot(self):
        # Unseen Camera C with zero labels
        tracks_b = [1, 2, 3, 4, 5]
        unseen_res = self.analytics.evaluate_unseen_camera(tracks_b)
        self.assertIn("unseen_idf1_pct", unseen_res)
        self.assertIn("unseen_precision_pct", unseen_res)
        self.assertIn("unseen_recall_pct", unseen_res)
        self.assertEqual(unseen_res["manual_calibration_time"], "0 minutes (Fully Automated Domain Adaptation)")

    def test_privacy_differential_privacy(self):
        # Differential Privacy & k-anonymity
        crop = np.full((80, 60, 3), (30, 200, 230), dtype=np.uint8)
        det = [VehicleDetection((50, 50, 60, 80), "bus", 0.9, crop)]
        self.tracker_a.update(det, timestamp=10.0)
        tracks_a = self.tracker_a.get_all_completed_tracks()
        analytics_out = self.analytics.compute_corridor_analytics(tracks_a, tracks_a, [])

        dp_report = self.privacy.generate_privacy_report(analytics_out, use_dp=True, epsilon=0.5)
        self.assertFalse(dp_report.empty)
        csv_str = self.privacy.export_csv_string(dp_report)
        self.assertIn("DP ε=0.5", csv_str)


    def test_tracking_momentum_and_spatial_affinity(self):
        crop = np.full((80, 60, 3), (30, 200, 230), dtype=np.uint8)
        # Vehicle moving from x=50 to x=80 (fast motion where strict IoU alone might drop track)
        det1 = [VehicleDetection((50, 50, 60, 80), "car", 0.9, crop)]
        self.tracker_a.update(det1, timestamp=1.0)

        det2 = [VehicleDetection((80, 50, 60, 80), "car", 0.9, crop)]
        active = self.tracker_a.update(det2, timestamp=1.1)

        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].track_id, "CAM-A-TRK-001")
        self.assertEqual(len(active[0].bboxes), 2)


    def test_vehicle_make_and_model_recognition(self):
        # Test Car Make & Model classification (e.g. Maruti Suzuki Dzire)
        white_sedan = np.full((80, 120, 3), (245, 245, 245), dtype=np.uint8)
        feat_car = self.extractor.extract(white_sedan, class_name="car")
        self.assertIn("vehicle_name", feat_car)
        self.assertIn("Maruti Suzuki Dzire", feat_car["vehicle_name"])
        self.assertEqual(feat_car["vehicle_make"], "Maruti Suzuki")
        self.assertEqual(feat_car["vehicle_model"], "Dzire")

        # Test Auto-Rickshaw Make & Model (Bajaj RE Compact)
        auto_crop = np.full((100, 90, 3), (30, 200, 230), dtype=np.uint8)
        feat_auto = self.extractor.extract(auto_crop, class_name="auto-rickshaw")
        self.assertIn("Bajaj RE Compact", feat_auto["vehicle_name"])
        self.assertEqual(feat_auto["vehicle_make"], "Bajaj")

        # Test Motorcycle Make & Model (Hero Splendor Plus)
        bike_crop = np.full((120, 60, 3), (50, 50, 50), dtype=np.uint8)
        feat_bike = self.extractor.extract(bike_crop, class_name="motorcycle")
        self.assertIn("Hero Splendor Plus", feat_bike["vehicle_name"])


    def test_robustness_and_edge_cases(self):
        # 1. Empty crop handling in feature extraction
        empty_feat = self.extractor.extract(None)
        self.assertEqual(empty_feat["dominant_color"], "Unknown")
        self.assertEqual(len(empty_feat["embedding_64d"]), 64)

        # 2. Zero-size crop
        zero_crop = np.zeros((0, 0, 3), dtype=np.uint8)
        zero_feat = self.extractor.extract(zero_crop)
        self.assertEqual(zero_feat["dominant_color"], "Unknown")

        # 3. Detector on empty frame
        empty_dets = self.detector.detect(None)
        self.assertEqual(empty_dets, [])

        # 4. Spatio-temporal score on negative delta_t (impossible reverse travel)
        st_rev = self.matcher.compute_spatio_temporal_score(-10.0)
        self.assertLessEqual(st_rev, 0.05)

        # 5. Visual similarity with missing features
        sim_empty = compute_visual_similarity({}, {})
        self.assertEqual(sim_empty, 0.0)


if __name__ == "__main__":
    unittest.main()
