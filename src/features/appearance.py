"""
MultiCam AI - Appearance Feature Extraction Engine
Extracts privacy-preserving vehicle appearance features:
- Dominant color profile (HSV median clustering)
- Geometric aspect ratio and profile
- 3-Stripe Spatial Appearance (Roof 30%, Body 45%, Chassis 25%)
- 64-dimensional normalized latent embedding vector
STRICT PRIVACY: Never uses license plates, faces, or optical character recognition.
"""

import cv2
import numpy as np
from src.features.make_model_classifier import VehicleMakeModelClassifier

COLOR_PALETTE = {
    "Obsidian Black": {"hex": "#1e2229", "h_range": (0, 180), "s_max": 255, "v_max": 45},
    "Pure White": {"hex": "#f5f5f5", "h_range": (0, 180), "s_max": 35, "v_min": 190},
    "Metallic Silver": {"hex": "#9fa3a9", "h_range": (0, 180), "s_max": 40, "v_range": (45, 190)},
    "Crimson Red": {"hex": "#c82828", "h_range": (170, 10), "s_min": 40, "v_min": 45},
    "Amber Orange": {"hex": "#d9731e", "h_range": (10, 25), "s_min": 40, "v_min": 45},
    "Golden Yellow": {"hex": "#dcb428", "h_range": (25, 38), "s_min": 40, "v_min": 45},
    "Forest Green": {"hex": "#288c3c", "h_range": (38, 85), "s_min": 40, "v_min": 45},
    "Cobalt Blue": {"hex": "#2864be", "h_range": (85, 135), "s_min": 40, "v_min": 45},
    "Deep Purple": {"hex": "#6e2878", "h_range": (135, 170), "s_min": 40, "v_min": 45},
}

class AppearanceFeatureExtractor:
    """Extracts spatial appearance embeddings and vehicle make/model from crops."""
    def __init__(self, target_size=(128, 128)):
        self.target_size = target_size
        self.mm_classifier = VehicleMakeModelClassifier()

    def extract(self, bgr_crop, class_name="car"):
        """
        Extracts appearance dictionary from vehicle image crop:
        Returns:
            dominant_color_name, dominant_hex, aspect_ratio,
            stripe_roof_hist, stripe_body_hist, stripe_chassis_hist,
            embedding_64d, vehicle_name, vehicle_make, vehicle_model, body_type
        """
        if bgr_crop is None or bgr_crop.size == 0:
            return self._empty_features()

        h, w = bgr_crop.shape[:2]
        aspect_ratio = float(w) / float(h) if h > 0 else 1.0

        # Resize to standard canonical size for part-based alignment
        resized = cv2.resize(bgr_crop, self.target_size, interpolation=cv2.INTER_AREA)
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)

        # 1. Compute Dominant Color
        color_name, hex_code = self._get_dominant_color(hsv)

        # 2. 3-Stripe Spatial Slices
        # Stripe 1: Roof / Windshield (Top 30%)
        # Stripe 2: Main Body Panels (Mid 45%)
        # Stripe 3: Chassis / Wheels (Bottom 25%)
        stripe_h = self.target_size[1]
        cut1 = int(stripe_h * 0.30)
        cut2 = int(stripe_h * 0.75)

        roof_hsv = hsv[0:cut1, :]
        body_hsv = hsv[cut1:cut2, :]
        chassis_hsv = hsv[cut2:stripe_h, :]

        hist_roof = self._calc_hist(roof_hsv, h_bins=12, s_bins=4)      # 48 bins
        hist_body = self._calc_hist(body_hsv, h_bins=16, s_bins=6)      # 96 bins
        hist_chassis = self._calc_hist(chassis_hsv, h_bins=8, s_bins=4) # 32 bins

        # 3. 64-Dimensional L2-Normalized Embedding Head
        embedding_64d = self._build_64d_embedding(hsv, hist_roof, hist_body, hist_chassis, aspect_ratio)

        # 4. Make & Model Recognition (VMMR)
        mm_res = self.mm_classifier.classify(bgr_crop, class_name=class_name, dominant_color=color_name, aspect_ratio=aspect_ratio)

        return {
            "dominant_color": color_name,
            "dominant_hex": hex_code,
            "aspect_ratio": round(aspect_ratio, 3),
            "hist_roof": hist_roof.tolist(),
            "hist_body": hist_body.tolist(),
            "hist_chassis": hist_chassis.tolist(),
            "embedding_64d": embedding_64d.tolist(),
            "make_model": mm_res,
            "vehicle_name": mm_res["full_name"],
            "vehicle_make": mm_res["make"],
            "vehicle_model": mm_res["model"],
            "body_type": mm_res["body_type"],
            "model_confidence": mm_res["confidence"],
            "visual_cues": mm_res["visual_cues"]
        }

    def _calc_hist(self, hsv_slice, h_bins=12, s_bins=4):
        """Calculates 2D Hue-Saturation normalized distribution."""
        if hsv_slice.size == 0:
            return np.zeros(h_bins * s_bins, dtype=np.float32)
        hist = cv2.calcHist([hsv_slice], [0, 1], None, [h_bins, s_bins], [0, 180, 0, 256])
        cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        return hist.flatten()

    def _get_dominant_color(self, hsv):
        """Identifies dominant color name and hex code."""
        h_med = np.median(hsv[:, :, 0])
        s_med = np.median(hsv[:, :, 1])
        v_med = np.median(hsv[:, :, 2])

        if v_med < 45:
            return "Obsidian Black", "#1e2229"
        if s_med < 35 and v_med > 190:
            return "Pure White", "#f5f5f5"
        if s_med < 40:
            return "Metallic Silver", "#9fa3a9"

        if h_med < 10 or h_med >= 170:
            return "Crimson Red", "#c82828"
        elif 10 <= h_med < 25:
            return "Amber Orange", "#d9731e"
        elif 25 <= h_med < 38:
            return "Golden Yellow", "#dcb428"
        elif 38 <= h_med < 85:
            return "Forest Green", "#288c3c"
        elif 85 <= h_med < 135:
            return "Cobalt Blue", "#2864be"
        return "Deep Purple", "#6e2878"

    def _build_64d_embedding(self, hsv, hist_roof, hist_body, hist_chassis, aspect_ratio):
        """
        Builds a compact 64-dimensional feature representation:
        - 16 dims from Roof Part
        - 32 dims from Body Panels
        - 14 dims from Chassis & Base
        - 2 dims from Aspect Ratio & Area Density
        L2-normalized onto unit hypersphere.
        """
        r_part = hist_roof[:16] if len(hist_roof) >= 16 else np.pad(hist_roof, (0, 16 - len(hist_roof)))
        b_part = hist_body[:32] if len(hist_body) >= 32 else np.pad(hist_body, (0, 32 - len(hist_body)))
        c_part = hist_chassis[:14] if len(hist_chassis) >= 14 else np.pad(hist_chassis, (0, 14 - len(hist_chassis)))

        # 2 geometric traits
        geom = np.array([
            min(1.0, max(0.0, (aspect_ratio - 0.4) / 2.0)),
            np.mean(hsv[:, :, 2]) / 255.0
        ], dtype=np.float32)

        emb = np.concatenate([r_part, b_part, c_part, geom])
        # L2-Normalize
        norm = np.linalg.norm(emb)
        if norm > 1e-6:
            emb = emb / norm
        return emb.astype(np.float32)

    def _empty_features(self):
        return {
            "dominant_color": "Unknown",
            "dominant_hex": "#777777",
            "aspect_ratio": 1.0,
            "hist_roof": [],
            "hist_body": [],
            "hist_chassis": [],
            "embedding_64d": np.zeros(64, dtype=np.float32).tolist(),
            "make_model": {"make": "Generic", "model": "Vehicle", "full_name": "Commercial Vehicle", "confidence": 0.5},
            "vehicle_name": "Commercial Vehicle",
            "vehicle_make": "Generic",
            "vehicle_model": "Vehicle",
            "body_type": "Vehicle",
            "model_confidence": 0.5,
            "visual_cues": []
        }


def compute_visual_similarity(feat_a, feat_b):
    """
    Computes visual cosine similarity between two appearance feature dictionaries.
    Range [0.0, 1.0].
    """
    if not feat_a or not feat_b:
        return 0.0

    emb_a = np.array(feat_a.get("embedding_64d", []))
    emb_b = np.array(feat_b.get("embedding_64d", []))

    if len(emb_a) != 64 or len(emb_b) != 64:
        return 0.5

    dot = np.dot(emb_a, emb_b)
    # Cosine distance bounded to [0.0, 1.0]
    cos_sim = float(max(0.0, min(1.0, (dot + 1.0) / 2.0)))

    # Exact color match bonus
    if feat_a.get("dominant_color") == feat_b.get("dominant_color"):
        cos_sim = min(1.0, cos_sim * 1.08)
    else:
        cos_sim = cos_sim * 0.88

    # Vehicle Make & Model compatibility bonus
    name_a = feat_a.get("vehicle_name")
    name_b = feat_b.get("vehicle_name")
    if name_a and name_b and name_a == name_b and "Generic" not in name_a:
        cos_sim = min(1.0, cos_sim * 1.06)

    return round(cos_sim, 4)
