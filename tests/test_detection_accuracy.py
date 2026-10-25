"""
MultiCam AI - Strict Detection & Tracking Accuracy Verification
Tests 5 Critical Scenarios:
1. Image containing a car -> Reports vehicle(s)
2. Image containing no vehicles -> Reports exactly 0 vehicles ("No vehicles detected")
3. Video containing vehicles -> Reports vehicles during transit
4. Video containing no vehicles -> Reports exactly 0 vehicles across all frames
5. Video where vehicles enter and leave -> Reports vehicle when present, exactly 0 when left (no stale detections)
"""

import unittest
import numpy as np
import cv2
import os

from src.detection.detector import HybridVehicleDetector, VehicleDetection
from src.tracking.tracker import MultiObjectTracker
from src.analytics.traffic_analytics import TrafficAnalyticsEngine

class TestStrictDetectionAccuracy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.detector = HybridVehicleDetector()
        cls.analytics = TrafficAnalyticsEngine(corridor_distance=850.0)

    def setUp(self):
        self.detector.reset()

    def test_1_image_containing_car(self):
        """Test with an image containing real cars: Must detect vehicle(s)."""
        img_path = "test_car_image.jpg"
        if not os.path.exists(img_path):
            img_path = os.path.join("smartcity", "test_car_image.jpg")
        self.assertTrue(os.path.exists(img_path), "test_car_image.jpg not found")

        frame = cv2.imread(img_path)
        self.assertIsNotNone(frame)

        dets = self.detector.detect(frame, conf_threshold=0.30)
        self.assertGreaterEqual(len(dets), 1, "Failed to detect car in image containing vehicles")
        for d in dets:
            self.assertIn(d.class_name, ["car", "bus", "truck", "motorcycle", "auto-rickshaw"])
            self.assertGreaterEqual(d.confidence, 0.30)
            x, y, w, h = d.bbox
            self.assertGreater(w, 0)
            self.assertGreater(h, 0)

    def test_2_image_containing_no_vehicles(self):
        """Test with images containing NO vehicles: Must return exactly 0 detections."""
        # 1. Uniform asphalt texture with lane lines
        asphalt = np.full((360, 640, 3), (60, 60, 60), dtype=np.uint8)
        cv2.line(asphalt, (0, 180), (640, 180), (240, 240, 240), 4)
        cv2.line(asphalt, (0, 300), (640, 300), (240, 240, 240), 4)
        dets_road = self.detector.detect(asphalt)
        self.assertEqual(len(dets_road), 0, f"Expected 0 detections on empty road, got {len(dets_road)}")

        # 2. Blank white canvas
        blank = np.full((400, 500, 3), 255, dtype=np.uint8)
        dets_blank = self.detector.detect(blank)
        self.assertEqual(len(dets_blank), 0, f"Expected 0 detections on blank image, got {len(dets_blank)}")

        # 3. Nature / foliage / sky background
        nature = np.zeros((360, 640, 3), dtype=np.uint8)
        nature[:180, :] = (235, 206, 135) # Sky blue
        nature[180:, :] = (34, 139, 34)   # Forest green
        dets_nature = self.detector.detect(nature)
        self.assertEqual(len(dets_nature), 0, f"Expected 0 detections on nature background, got {len(dets_nature)}")

    def test_3_video_containing_vehicles(self):
        """Test with video containing vehicles: Must detect and track actual vehicles."""
        video_path = os.path.join("backend", "uploads", "custom_cam_a.mp4")
        if not os.path.exists(video_path):
            video_path = "demo_cam_a.mp4"

        cap = cv2.VideoCapture(video_path)
        tracker = MultiObjectTracker(camera_id="CAM-TEST")
        total_detections = 0
        frames_checked = 0

        # Sample 10 frames
        while cap.isOpened() and frames_checked < 10:
            ret, frame = cap.read()
            if not ret: break
            frames_checked += 1
            dets = self.detector.detect(frame, conf_threshold=0.30)
            active_tracks = tracker.update(dets, timestamp=frames_checked * 0.04)
            total_detections += len(dets)
            self.assertEqual(len(active_tracks), len(dets), "Active tracks in frame must match current frame detections exactly")

        cap.release()
        self.assertGreater(total_detections, 0, "Video with vehicles must report detections")
        self.assertGreater(len(tracker.get_all_completed_tracks()), 0, "Tracker must record completed vehicle tracks")

    def test_4_video_containing_no_vehicles(self):
        """Test with video containing NO vehicles: Must report exactly 0 detections across all frames."""
        tracker = MultiObjectTracker(camera_id="CAM-EMPTY")
        
        # Simulate 15 frames of empty road with moving shadows/lighting changes
        for f_idx in range(15):
            frame = np.full((360, 640, 3), 65, dtype=np.uint8)
            cv2.line(frame, (100, 0), (100, 360), (220, 220, 220), 2)
            cv2.line(frame, (540, 0), (540, 360), (220, 220, 220), 2)
            cv2.circle(frame, (30 + f_idx * 3, 40), 25, (40, 45, 40), -1)

            dets = self.detector.detect(frame)
            active_tracks = tracker.update(dets, timestamp=f_idx * 0.1)

            self.assertEqual(len(dets), 0, f"Frame {f_idx}: Detected fake vehicle in empty video!")
            self.assertEqual(len(active_tracks), 0, f"Frame {f_idx}: Tracker reported stale or fake track in empty video!")

        self.assertEqual(len(tracker.get_all_completed_tracks()), 0, "Empty video must yield 0 completed tracks")

    def test_5_video_vehicles_enter_and_leave(self):
        """Test video where vehicles enter and leave: Must NOT reuse stale detections when vehicle departs."""
        tracker = MultiObjectTracker(camera_id="CAM-ENTER-EXIT")
        crop = np.full((50, 70, 3), (200, 200, 200), dtype=np.uint8)

        # Stage 1 (Frames 1-2): No vehicles yet (Empty road)
        for f in range(1, 3):
            active = tracker.update([], timestamp=f * 0.1)
            self.assertEqual(len(active), 0, f"Stage 1 Frame {f} must have 0 active detections")

        # Stage 2 (Frames 3-5): Vehicle enters and is present
        for f in range(3, 6):
            det = [VehicleDetection((100 + f * 10, 150, 70, 50), "car", 0.90, crop)]
            active = tracker.update(det, timestamp=f * 0.1)
            self.assertEqual(len(active), 1, f"Stage 2 Frame {f} must report exactly 1 vehicle")
            self.assertEqual(active[0].track_id, "CAM-ENTER-EXIT-TRK-001")

        # Stage 3 (Frames 6-10): Vehicle LEAVES the frame
        for f in range(6, 11):
            active = tracker.update([], timestamp=f * 0.1)
            # Must NOT reuse stale detection from frame 5!
            self.assertEqual(len(active), 0, f"Stage 3 Frame {f} must report 0 vehicles after vehicle left frame!")

        # Completed tracks must reflect the 1 vehicle that traversed
        completed = tracker.get_all_completed_tracks()
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].track_id, "CAM-ENTER-EXIT-TRK-001")
        self.assertEqual(len(completed[0].bboxes), 3)

    def test_6_analytics_on_empty_feeds(self):
        """Test analytics engine when 0 vehicles are present: Must not invent speeds or flows."""
        res = self.analytics.compute_corridor_analytics([], [], [])
        self.assertEqual(res["total_ingress"], 0)
        self.assertEqual(res["total_egress"], 0)
        self.assertEqual(res["verified_matches"], 0)
        self.assertEqual(res["avg_speed"], 0.0)
        self.assertEqual(res["flow_rate_vph"], 0)
        self.assertIn("Standby", res["level_of_service"])

        night_res = self.analytics.compute_night_metrics([], [], [])
        self.assertEqual(night_res["id_tp"], 0)
        self.assertEqual(night_res["idf1_percent"], 0.0)

        fail_res = self.analytics.simulate_camera_failure([], [])
        self.assertEqual(fail_res["estimated_corridor_flow_vph"], 0)

if __name__ == "__main__":
    unittest.main()
