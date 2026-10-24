"""
Feature Extractor Module
Extracts appearance-based visual signatures for vehicles without license plates.
Uses multi-part HSV spatial color histograms, aspect ratio, and dominant color clustering.
"""

import cv2
import numpy as np


# Common vehicle color reference table for human-readable labelling
COLOR_REFERENCES = {
    "White": (240, 240, 240),
    "Silver / Grey": (170, 175, 180),
    "Dark Charcoal / Black": (35, 38, 42),
    "Navy / Dark Blue": (30, 50, 110),
    "Blue": (40, 100, 190),
    "Crimson / Red": (180, 40, 40),
    "Burgundy / Maroon": (110, 25, 40),
    "Golden / Yellow": (210, 180, 50),
    "Auto Green": (35, 120, 60),
    "Emerald / Green": (35, 120, 60),
    "Bronze / Brown": (120, 75, 45),
}


def estimate_vehicle_type(aspect_ratio, area_pixels, w=0, h=0):
    """
    Estimates vehicle body type supporting Indian mixed traffic:
    - Two-Wheeler (Motorcycle / Scooter): very narrow W/H < 0.50
    - Auto-Rickshaw (3-Wheeler): compact boxy/trapezoidal 0.50 <= W/H < 0.85 and small footprint
    - Passenger Car / Hatchback: standard 0.85 <= W/H < 1.45
    - SUV / Van: boxy taller passenger 1.45 <= W/H < 1.85
    - Commercial Mini-Truck (Tata Ace): distinctive cab + open back
    - City Bus / Heavy Truck: large area and elongation
    """
    if w > 0 and h > 0:
        if w < 30 and h > 40:
            return "Two-Wheeler (Bike/Scooter)"
        if 30 <= w <= 46 and 40 <= h <= 65:
            return "Auto-Rickshaw (3-Wheeler)"
        if h > 110:
            return "City Bus / Heavy Vehicle"

    if aspect_ratio < 0.48:
        return "Two-Wheeler (Bike/Scooter)"
    elif 0.48 <= aspect_ratio < 0.82:
        return "Auto-Rickshaw (3-Wheeler)"
    elif 0.82 <= aspect_ratio < 1.40:
        return "Commercial Mini-Truck"
    elif 1.40 <= aspect_ratio < 1.85:
        return "Car / Hatchback"
    elif 1.85 <= aspect_ratio < 2.40:
        return "SUV / MUV"
    else:
        return "City Bus / Commercial"


def get_dominant_color(bgr_image):
    """
    Calculates dominant RGB color by sampling center pixels
    (avoiding background edges) and finds the nearest friendly color name.
    """
    if bgr_image is None or bgr_image.size == 0:
        return "#808080", "Unknown"

    # Crop inner 60% to avoid background road pixels around vehicle edges
    h, w = bgr_image.shape[:2]
    inner = bgr_image[int(h * 0.2):int(h * 0.8), int(w * 0.2):int(w * 0.8)]
    if inner.size == 0:
        inner = bgr_image

    rgb_inner = cv2.cvtColor(inner, cv2.COLOR_BGR2RGB)
    mean_rgb = np.mean(rgb_inner.reshape(-1, 3), axis=0)
    r, g, b = int(mean_rgb[0]), int(mean_rgb[1]), int(mean_rgb[2])
    hex_code = f"#{r:02x}{g:02x}{b:02x}"

    # Match to nearest reference color
    best_name = "Custom Color"
    min_dist = float("inf")
    for name, ref_rgb in COLOR_REFERENCES.items():
        dist = np.linalg.norm(np.array([r, g, b]) - np.array(ref_rgb))
        if dist < min_dist:
            min_dist = dist
            best_name = name

    return hex_code, best_name


def compute_stripe_histogram(hsv_crop, h_bins=16, s_bins=8):
    """
    Calculates a 2D normalized Hue-Saturation color histogram for an image stripe.
    Hue range: [0, 180), Saturation range: [0, 256).
    """
    if hsv_crop is None or hsv_crop.size == 0:
        return np.zeros(h_bins * s_bins, dtype=np.float32)

    hist = cv2.calcHist(
        [hsv_crop],
        [0, 1],
        None,
        [h_bins, s_bins],
        [0, 180, 0, 256]
    )
    cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    return hist.flatten()


def extract_vehicle_features(bgr_crop):
    """
    Extracts multi-part visual feature signature from a cropped vehicle image:
    1. Spatial partition: Top (roof/windshield), Mid (doors/hood), Bot (bumper/wheels)
    2. Hue-Saturation histograms for each stripe
    3. Aspect ratio (W / H)
    4. Dominant color hex & name
    5. Estimated vehicle category
    6. 64-dimensional L2-normalized feature embedding vector (model latent space)
    """
    if bgr_crop is None or bgr_crop.size == 0:
        return None

    h, w = bgr_crop.shape[:2]
    if h < 10 or w < 10:
        return None

    aspect_ratio = round(float(w) / float(h), 3)
    vehicle_type = estimate_vehicle_type(aspect_ratio, w * h, w, h)
    dom_hex, dom_name = get_dominant_color(bgr_crop)

    # Convert to HSV color space for illumination robustness
    hsv = cv2.cvtColor(bgr_crop, cv2.COLOR_BGR2HSV)

    # 3-tier vertical spatial stripes:
    # Top 30%: Roof, roof racks, upper glass
    # Mid 45%: Body paint, door panels, hood
    # Bot 25%: Tires, lower bumper, road shadow
    y_top = int(h * 0.30)
    y_mid = int(h * 0.75)

    top_stripe = hsv[0:y_top, :]
    mid_stripe = hsv[y_top:y_mid, :]
    bot_stripe = hsv[y_mid:h, :]

    hist_top = compute_stripe_histogram(top_stripe, h_bins=8, s_bins=4)   # 32 values
    hist_mid = compute_stripe_histogram(mid_stripe, h_bins=8, s_bins=4)   # 32 values
    hist_bot = compute_stripe_histogram(bot_stripe, h_bins=8, s_bins=4)   # 32 values

    # Global color histogram
    hist_global = compute_stripe_histogram(hsv, h_bins=8, s_bins=4)

    # Build 64-dimensional normalized latent feature embedding vector:
    # Slice 1: Mid stripe appearance (24 elements) - most discriminative
    # Slice 2: Top stripe appearance (16 elements)
    # Slice 3: Bot stripe appearance (12 elements)
    # Slice 4: Geometry & RGB color cues (12 elements)
    mid_slice = hist_mid[:24]
    top_slice = hist_top[:16]
    bot_slice = hist_bot[:12]

    # Geometric & color cues
    rgb_crop = cv2.cvtColor(bgr_crop, cv2.COLOR_BGR2RGB)
    mean_rgb = np.mean(rgb_crop, axis=(0, 1)) / 255.0
    std_rgb = np.std(rgb_crop, axis=(0, 1)) / 255.0
    geom_cues = np.array([
        min(1.0, aspect_ratio / 3.0),
        min(1.0, (w * h) / 15000.0),
        mean_rgb[0], mean_rgb[1], mean_rgb[2],
        std_rgb[0], std_rgb[1], std_rgb[2],
        1.0 if "Two-Wheeler" in vehicle_type else 0.0,
        1.0 if "Auto-Rickshaw" in vehicle_type else 0.0,
        1.0 if "Bus" in vehicle_type else 0.0,
        1.0 if "Car" in vehicle_type else 0.0
    ], dtype=np.float32)

    raw_embed = np.concatenate([mid_slice, top_slice, bot_slice, geom_cues])
    norm_val = np.linalg.norm(raw_embed)
    embedding_64d = (raw_embed / (norm_val + 1e-7)).tolist()
    embedding_64d = [round(float(v), 4) for v in embedding_64d]

    # Compact feature dictionary
    return {
        "aspect_ratio": aspect_ratio,
        "width": w,
        "height": h,
        "dominant_color_hex": dom_hex,
        "dominant_color_name": dom_name,
        "vehicle_type": vehicle_type,
        "hist_top": hist_top.tolist(),
        "hist_mid": hist_mid.tolist(),
        "hist_bot": hist_bot.tolist(),
        "hist_global": hist_global.tolist(),
        "embedding_64d": embedding_64d
    }


def compare_feature_signatures(feat_a, feat_b):
    """
    Computes visual similarity score in [0.0, 1.0] between two vehicle feature signatures.
    Uses weighted multi-stripe histogram correlation + aspect ratio penalty.
    """
    if not feat_a or not feat_b:
        return 0.0

    # Stripe histogram correlation (using cv2.HISTCMP_CORREL)
    def stripe_corr(arr_a, arr_b):
        a = np.array(arr_a, dtype=np.float32)
        b = np.array(arr_b, dtype=np.float32)
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        # Cosine similarity bounded in [0, 1]
        cosine = float(np.dot(a, b) / denom)
        return max(0.0, min(1.0, cosine))

    sim_top = stripe_corr(feat_a["hist_top"], feat_b["hist_top"])
    sim_mid = stripe_corr(feat_a["hist_mid"], feat_b["hist_mid"])
    sim_bot = stripe_corr(feat_a["hist_bot"], feat_b["hist_bot"])
    sim_global = stripe_corr(feat_a["hist_global"], feat_b["hist_global"])

    # Mid stripe (body panels) carries the most vehicle identity weight
    weighted_color_sim = (
        0.20 * sim_top +
        0.45 * sim_mid +
        0.15 * sim_bot +
        0.20 * sim_global
    )

    # Aspect ratio comparison
    ar_a = feat_a["aspect_ratio"]
    ar_b = feat_b["aspect_ratio"]
    ar_diff = abs(ar_a - ar_b) / max(ar_a, ar_b, 0.01)
    ar_sim = max(0.0, 1.0 - (ar_diff * 1.5))

    # Type agreement bonus/penalty
    type_match = 1.0 if feat_a["vehicle_type"] == feat_b["vehicle_type"] else 0.70

    # Final combined visual similarity
    visual_similarity = (0.70 * weighted_color_sim + 0.30 * ar_sim) * type_match
    return round(float(visual_similarity), 3)
