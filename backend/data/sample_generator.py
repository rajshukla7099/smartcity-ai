"""
Synthetic Surveillance Corridor Generator
Generates realistic multi-camera traffic imagery and ground-truth tracklets
for non-overlapping camera re-identification testing.
Clearly designated as DEMO DATA for hackathon demonstration.
"""

import os
import cv2
import numpy as np
from core.feature_extractor import extract_vehicle_features, compare_feature_signatures
from core.tracker import VehicleTracklet


def create_road_canvas(w=640, h=360, camera_id="CAM-A", location_name="Junction 4th Ave (North)"):
    """Creates a realistic asphalt roadway scene with lane markings and CCTV noise."""
    canvas = np.zeros((h, w, 3), dtype=np.uint8)

    # Road surface (dark grey asphalt with slight noise)
    base_gray = 42 if "CAM-A" in camera_id else 48
    canvas[:, :] = (base_gray, base_gray + 2, base_gray + 4)

    # Add subtle sensor noise
    noise = np.random.normal(0, 3, (h, w, 3)).astype(np.int16)
    canvas = np.clip(canvas.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Sidewalks / curbs
    curb_color = (75, 78, 80) if "CAM-A" in camera_id else (85, 88, 90)
    cv2.rectangle(canvas, (0, 0), (70, h), curb_color, -1)
    cv2.rectangle(canvas, (w - 70, 0), (w, h), curb_color, -1)

    # Curb edges
    cv2.line(canvas, (70, 0), (70, h), (120, 120, 120), 2)
    cv2.line(canvas, (w - 70, 0), (w - 70, h), (120, 120, 120), 2)

    # Center broken lane markings
    lane_x = w // 2
    dash_h = 30
    gap = 25
    for y in range(0, h, dash_h + gap):
        cv2.line(canvas, (lane_x, y), (lane_x, y + dash_h), (210, 210, 180), 2)

    # Lane boundaries
    cv2.line(canvas, (80, 0), (80, h), (200, 200, 200), 1)
    cv2.line(canvas, (w - 80, 0), (w - 80, h), (200, 200, 200), 1)

    # CCTV metadata watermark on top
    cv2.rectangle(canvas, (0, 0), (w, 24), (15, 23, 42), -1)
    cv2.putText(
        canvas,
        f"[DEMO BENCHMARK] {camera_id}: {location_name} | RES: 640x360 | 30 FPS",
        (10, 17),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        (180, 200, 220),
        1,
        cv2.LINE_AA
    )

    return canvas


def draw_realistic_vehicle(canvas, x, y, w, h, body_bgr, roof_bgr=None, vehicle_type="car"):
    """
    Renders realistic vehicle silhouettes authentic to Indian mixed traffic:
    - Auto-Rickshaw: yellow canopy, green body, 3-wheel geometry
    - Two-Wheeler: slim commuter bike profile with rider
    - Bus: extended transit chassis with rows of side windows
    - Commercial Mini-Truck (Tata Ace): flat cab + utility cargo bay
    - Passenger Hatchbacks / Sedans / SUVs
    """
    if roof_bgr is None:
        roof_bgr = body_bgr

    # Cast subtle road contact shadow
    shadow = np.zeros_like(canvas)
    cv2.ellipse(shadow, (x + w // 2, y + h - 2), (w // 2 + 4, max(4, h // 10)), 0, 0, 360, (20, 20, 20), -1)
    cv2.addWeighted(canvas, 1.0, shadow, 0.45, 0, canvas)

    v_lower = vehicle_type.lower()

    if "two-wheeler" in v_lower or "bike" in v_lower:
        # Two-Wheeler: slim profile
        # Wheels (front & back)
        cv2.circle(canvas, (x + w // 2, y + 6), 4, (20, 20, 20), -1)
        cv2.circle(canvas, (x + w // 2, y + h - 6), 4, (20, 20, 20), -1)
        # Bike frame / fuel tank
        cv2.rectangle(canvas, (x + 4, y + 10), (x + w - 4, y + h - 10), body_bgr, -1)
        # Rider helmet & shoulders
        cv2.circle(canvas, (x + w // 2, y + h // 2 - 4), 6, roof_bgr, -1)
        cv2.rectangle(canvas, (x + 2, y + h // 2), (x + w - 2, y + h // 2 + 10), (35, 35, 40), -1)
        # Handlebars
        cv2.line(canvas, (x, y + 14), (x + w, y + 14), (160, 160, 160), 2)
        return

    if "auto-rickshaw" in v_lower or "3-wheeler" in v_lower:
        # Auto-Rickshaw: iconic yellow roof / green body
        # 3 wheels (1 front centered, 2 rear)
        cv2.circle(canvas, (x + w // 2, y + 4), 4, (25, 25, 25), -1)
        cv2.rectangle(canvas, (x - 2, y + h - 12), (x + 4, y + h - 2), (25, 25, 25), -1)
        cv2.rectangle(canvas, (x + w - 4, y + h - 12), (x + w + 2, y + h - 2), (25, 25, 25), -1)
        # Lower Green/Black chassis
        cv2.rectangle(canvas, (x, y + 8), (x + w, y + h), body_bgr, -1)
        # Front taper
        pts = np.array([[x, y + 12], [x + w // 2, y], [x + w, y + 12]], np.int32)
        cv2.fillPoly(canvas, [pts], body_bgr)
        # Yellow Canopy Top
        canopy_y1 = y + int(h * 0.22)
        canopy_y2 = y + int(h * 0.78)
        cv2.rectangle(canvas, (x + 2, canopy_y1), (x + w - 2, canopy_y2), roof_bgr, -1)
        # Windshield
        cv2.rectangle(canvas, (x + 3, y + 12), (x + w - 3, canopy_y1), (40, 50, 60), -1)
        cv2.rectangle(canvas, (x, y), (x + w, y + h), (30, 30, 30), 1)
        return

    if "bus" in v_lower:
        # City Bus: elongated transit vehicle
        # Tires (4 corners)
        cv2.rectangle(canvas, (x - 3, y + 15), (x + 3, y + 35), (20, 20, 20), -1)
        cv2.rectangle(canvas, (x + w - 3, y + 15), (x + w + 3, y + 35), (20, 20, 20), -1)
        cv2.rectangle(canvas, (x - 3, y + h - 40), (x + 3, y + h - 20), (20, 20, 20), -1)
        cv2.rectangle(canvas, (x + w - 3, y + h - 40), (x + w + 3, y + h - 20), (20, 20, 20), -1)
        # Body
        cv2.rectangle(canvas, (x, y), (x + w, y + h), body_bgr, -1)
        cv2.rectangle(canvas, (x, y), (x + w, y + h), (40, 40, 40), 1)
        # Roof panel
        cv2.rectangle(canvas, (x + 4, y + 15), (x + w - 4, y + h - 15), roof_bgr, -1)
        # Multi-window panels
        for wy in range(y + 20, y + h - 20, 18):
            cv2.rectangle(canvas, (x + 2, wy), (x + 5, wy + 12), (30, 45, 60), -1)
            cv2.rectangle(canvas, (x + w - 5, wy), (x + w - 2, wy + 12), (30, 45, 60), -1)
        return

    if "mini-truck" in v_lower or "chhota hathi" in v_lower:
        # Commercial Mini-Truck (Tata Ace): Forward Cab + Cargo Bed
        # Front Cab (white/body)
        cab_h = int(h * 0.38)
        cv2.rectangle(canvas, (x, y), (x + w, y + cab_h), body_bgr, -1)
        cv2.rectangle(canvas, (x + 3, y + 8), (x + w - 3, y + cab_h - 4), (40, 50, 60), -1) # Windshield
        # Cargo Bay (open utility bed)
        cv2.rectangle(canvas, (x, y + cab_h + 2), (x + w, y + h), roof_bgr, -1)
        # Tailgate border
        cv2.rectangle(canvas, (x + 2, y + cab_h + 4), (x + w - 2, y + h - 2), (30, 30, 30), 1)
        return

    # Standard Passenger Car / Hatchback / SUV
    tire_w = max(4, w // 8)
    tire_h = max(6, h // 5)
    cv2.rectangle(canvas, (x - 2, y + h // 4), (x + tire_w, y + h // 4 + tire_h), (20, 20, 20), -1)
    cv2.rectangle(canvas, (x + w - tire_w, y + h // 4), (x + w + 2, y + h // 4 + tire_h), (20, 20, 20), -1)
    cv2.rectangle(canvas, (x - 2, y + int(h * 0.7)), (x + tire_w, y + int(h * 0.7) + tire_h), (20, 20, 20), -1)
    cv2.rectangle(canvas, (x + w - tire_w, y + int(h * 0.7)), (x + w + 2, y + int(h * 0.7) + tire_h), (20, 20, 20), -1)

    # Vehicle main body
    cv2.rectangle(canvas, (x, y), (x + w, y + h), body_bgr, -1)
    cv2.rectangle(canvas, (x, y), (x + w, y + h), (40, 40, 40), 1)

    # Cabin / Roof (darkened windows + roof color)
    cabin_x = x + int(w * 0.12)
    cabin_y = y + int(h * 0.28)
    cabin_w = int(w * 0.76)
    cabin_h = int(h * 0.45)
    cv2.rectangle(canvas, (cabin_x, cabin_y), (cabin_x + cabin_w, cabin_y + cabin_h), (35, 45, 55), -1)
    cv2.rectangle(canvas, (cabin_x + 4, cabin_y + 6), (cabin_x + cabin_w - 4, cabin_y + cabin_h - 6), roof_bgr, -1)

    # Headlights & Taillights
    headlight_color = (210, 240, 255)
    taillight_color = (30, 30, 210)
    cv2.circle(canvas, (x + 4, y + 4), 3, headlight_color, -1)
    cv2.circle(canvas, (x + w - 4, y + 4), 3, headlight_color, -1)
    cv2.circle(canvas, (x + 4, y + h - 4), 3, taillight_color, -1)
    cv2.circle(canvas, (x + w - 4, y + h - 4), 3, taillight_color, -1)


# Preset test vehicles authentic to Indian Smart City Corridor (SC-01 Problem Statement)
DEMO_VEHICLES = [
    {
        "id": "V-01",
        "name": "Bajaj Auto-Rickshaw (3-Wheeler)",
        "type": "Auto-Rickshaw (3-Wheeler)",
        "body_bgr": (35, 115, 45),     # Classic Auto Green
        "roof_bgr": (40, 205, 245),    # Iconic Mustard Yellow Canopy
        "w": 38, "h": 58,
        "lane_a": 1, "lane_b": 1,
        "entry_a": 10.0, "exit_a": 15.2,
        "entry_b": 72.0, "exit_b": 77.5,
        "y_a": 110, "y_b": 130,
        "transit_ground_truth": 56.8,
        "is_reid_match": True,
        "notes": "Classic Indian Auto-Rickshaw. High spatial contrast (Yellow canopy vs Green apron)."
    },
    {
        "id": "V-02",
        "name": "Commuter Motorcycle (125cc)",
        "type": "Two-Wheeler (Bike/Scooter)",
        "body_bgr": (30, 30, 35),      # Charcoal Black
        "roof_bgr": (180, 40, 40),     # Red helmet
        "w": 20, "h": 46,
        "lane_a": 2, "lane_b": 2,
        "entry_a": 16.5, "exit_a": 21.0,
        "entry_b": 68.0, "exit_b": 72.4,
        "y_a": 180, "y_b": 195,
        "transit_ground_truth": 47.0,
        "is_reid_match": True,
        "notes": "Fast two-wheeler lane filtering through corridor. High transit speed (65 km/h)."
    },
    {
        "id": "V-03",
        "name": "Maruti Suzuki Swift (White)",
        "type": "Car / Hatchback",
        "body_bgr": (240, 240, 240),
        "roof_bgr": (240, 240, 240),
        "w": 52, "h": 82,
        "lane_a": 1, "lane_b": 1,
        "entry_a": 24.0, "exit_a": 29.5,
        "entry_b": 84.0, "exit_b": 89.6,
        "y_a": 220, "y_b": 240,
        "transit_ground_truth": 54.5,
        "is_reid_match": True,
        "notes": "India's highest volume passenger hatchback. Evaluates near-identical vehicle differentiation."
    },
    {
        "id": "V-04",
        "name": "Hyundai i20 (Crimson Red)",
        "type": "Car / Hatchback",
        "body_bgr": (40, 35, 195),
        "roof_bgr": (40, 35, 195),
        "w": 52, "h": 80,
        "lane_a": 2, "lane_b": 2,
        "entry_a": 32.0, "exit_a": 37.2,
        "entry_b": 95.0, "exit_b": 100.2,
        "y_a": 60, "y_b": 70,
        "transit_ground_truth": 57.8,
        "is_reid_match": True,
        "notes": "Vibrant red compact car. High chromatic saliency."
    },
    {
        "id": "V-05",
        "name": "Tata Ace 'Chhota Hathi' (Mini-Truck)",
        "type": "Commercial Mini-Truck",
        "body_bgr": (230, 230, 230),    # White Cab
        "roof_bgr": (170, 70, 30),      # Blue Cargo Utility Bed
        "w": 46, "h": 72,
        "lane_a": 1, "lane_b": 2,
        "entry_a": 40.0, "exit_a": 46.2,
        "entry_b": 112.0, "exit_b": 118.5,
        "y_a": 140, "y_b": 160,
        "transit_ground_truth": 65.8,
        "is_reid_match": True,
        "notes": "Standard Indian commercial mini-truck. Two-tone cab/utility cargo split."
    },
    {
        "id": "V-06",
        "name": "State City Transit Bus",
        "type": "City Bus / Heavy Vehicle",
        "body_bgr": (190, 85, 30),      # Deep Transport Blue
        "roof_bgr": (220, 225, 230),    # White roof
        "w": 58, "h": 125,
        "lane_a": 2, "lane_b": 2,
        "entry_a": 48.0, "exit_a": 55.4,
        "entry_b": 128.0, "exit_b": 135.8,
        "y_a": 240, "y_b": 220,
        "transit_ground_truth": 72.6,
        "is_reid_match": True,
        "notes": "Large municipal bus, slower progression through junction queues."
    },
    {
        "id": "V-07",
        "name": "Distractor White Swift (Diverted at Market Alley)",
        "type": "Car / Hatchback",
        "body_bgr": (235, 235, 235),
        "roof_bgr": (235, 235, 235),
        "w": 52, "h": 82,
        "lane_a": 1, "lane_b": 0,
        "entry_a": 52.0, "exit_a": 57.0,
        "entry_b": None, "exit_b": None,
        "y_a": 280, "y_b": 0,
        "transit_ground_truth": None,
        "is_reid_match": False,
        "notes": "Visually near-identical to V-03, but turned into local bazaar alley before Cam B. Negative control."
    },
    {
        "id": "V-08",
        "name": "Distractor Auto-Rickshaw (Side Colony Entry)",
        "type": "Auto-Rickshaw (3-Wheeler)",
        "body_bgr": (35, 115, 45),
        "roof_bgr": (45, 45, 50),       # Black canopy (contrasts with yellow V-01)
        "w": 38, "h": 58,
        "lane_a": 0, "lane_b": 1,
        "entry_a": None, "exit_a": None,
        "entry_b": 90.0, "exit_b": 95.4,
        "y_a": 0, "y_b": 90,
        "transit_ground_truth": None,
        "is_reid_match": False,
        "notes": "Entered Camera B from a residential side street. Black canopy tests part-based stripe discrimination."
    },
    {
        "id": "V-09",
        "name": "Mahindra Scorpio SUV (Midnight Blue)",
        "type": "SUV / MUV",
        "body_bgr": (95, 45, 30),
        "roof_bgr": (80, 35, 20),
        "w": 58, "h": 94,
        "lane_a": 2, "lane_b": 1,
        "entry_a": 60.0, "exit_a": 66.0,
        "entry_b": 120.0, "exit_b": 126.2,
        "y_a": 160, "y_b": 170,
        "transit_ground_truth": 54.0,
        "is_reid_match": True,
        "notes": "Dominant dark blue SUV silhouette with prominent roof rails."
    }
]


def generate_demo_dataset(output_dir):
    """
    Builds the complete demo corridor dataset:
    - Synthesizes Camera A and Camera B corridor frames
    - Crops individual vehicles
    - Extracts authentic visual feature embeddings
    - Constructs ground truth tracklets
    """
    os.makedirs(output_dir, exist_ok=True)
    cam_a_dir = os.path.join(output_dir, "cam_a")
    cam_b_dir = os.path.join(output_dir, "cam_b")
    crops_dir = os.path.join(output_dir, "crops")
    os.makedirs(cam_a_dir, exist_ok=True)
    os.makedirs(cam_b_dir, exist_ok=True)
    os.makedirs(crops_dir, exist_ok=True)

    # Lane X center coords
    # Lane 1 (left lane): x ~ 180
    # Lane 2 (right lane): x ~ 380
    lane_x_map = {1: 180, 2: 380}

    cam_a_tracklets = []
    cam_b_tracklets = []

    # 1. Render Camera A Overview Frame
    frame_a = create_road_canvas(640, 360, "CAM-A", "Junction 4th Ave (North Approach)")
    # 2. Render Camera B Overview Frame
    frame_b = create_road_canvas(640, 360, "CAM-B", "Junction 5th Ave (South Exit - 850m)")

    for v in DEMO_VEHICLES:
        # Camera A presence
        if v["lane_a"] > 0:
            cx = lane_x_map[v["lane_a"]]
            w, h = v["w"], v["h"]
            x = cx - w // 2
            y = v["y_a"]
            draw_realistic_vehicle(frame_a, x, y, w, h, v["body_bgr"], v["roof_bgr"], v["type"])

            # Crop vehicle
            crop_a = frame_a[y:y+h, x:x+w].copy()
            crop_a_filename = f"crop_{v['id']}_cam_a.jpg"
            crop_a_path = os.path.join(crops_dir, crop_a_filename)
            cv2.imwrite(crop_a_path, crop_a)

            feat_a = extract_vehicle_features(crop_a)

            # Build tracklet object
            t_a = VehicleTracklet(
                track_id=f"CAM-A-{v['id']}",
                camera_id="CAM-A",
                initial_bbox=(x, y, w, h),
                frame_idx=int(v["entry_a"] * 30),
                timestamp_sec=v["entry_a"],
                crop_img=crop_a,
                features=feat_a
            )
            t_a.last_timestamp = v["exit_a"]
            t_a.last_frame = int(v["exit_a"] * 30)
            t_a.bboxes.append((x, y + 25, w, h))
            t_a.is_completed = True
            cam_a_tracklets.append(t_a)

        # Camera B presence
        if v["lane_b"] > 0:
            cx = lane_x_map[v["lane_b"]]
            w, h = v["w"], v["h"]
            x = cx - w // 2
            y = v["y_b"]
            # Apply slight lighting / angle variation typical of non-overlapping CCTV
            bgr_shifted = tuple(min(255, max(0, int(c * 0.95 + 8))) for c in v["body_bgr"])
            roof_shifted = tuple(min(255, max(0, int(c * 0.95 + 8))) for c in v["roof_bgr"])
            draw_realistic_vehicle(frame_b, x, y, w, h, bgr_shifted, roof_shifted, v["type"])

            crop_b = frame_b[y:y+h, x:x+w].copy()
            crop_b_filename = f"crop_{v['id']}_cam_b.jpg"
            crop_b_path = os.path.join(crops_dir, crop_b_filename)
            cv2.imwrite(crop_b_path, crop_b)

            feat_b = extract_vehicle_features(crop_b)

            t_b = VehicleTracklet(
                track_id=f"CAM-B-{v['id']}",
                camera_id="CAM-B",
                initial_bbox=(x, y, w, h),
                frame_idx=int(v["entry_b"] * 30),
                timestamp_sec=v["entry_b"],
                crop_img=crop_b,
                features=feat_b
            )
            t_b.last_timestamp = v["exit_b"]
            t_b.last_frame = int(v["exit_b"] * 30)
            t_b.bboxes.append((x, y + 25, w, h))
            t_b.is_completed = True
            cam_b_tracklets.append(t_b)

    # Save overview frames
    cam_a_path = os.path.join(cam_a_dir, "overview.jpg")
    cam_b_path = os.path.join(cam_b_dir, "overview.jpg")
    cv2.imwrite(cam_a_path, frame_a)
    cv2.imwrite(cam_b_path, frame_b)

    return {
        "cam_a_path": cam_a_path,
        "cam_b_path": cam_b_path,
        "cam_a_tracklets": cam_a_tracklets,
        "cam_b_tracklets": cam_b_tracklets
    }


def generate_random_dataset(output_dir):
    """
    Synthesizes a completely randomized traffic scenario on-demand:
    Randomizes vehicle types, body paint hues, corridor transit velocities,
    and spatio-temporal arrival times.
    """
    import random
    os.makedirs(output_dir, exist_ok=True)
    cam_a_dir = os.path.join(output_dir, "cam_a")
    cam_b_dir = os.path.join(output_dir, "cam_b")
    crops_dir = os.path.join(output_dir, "crops")
    os.makedirs(cam_a_dir, exist_ok=True)
    os.makedirs(cam_b_dir, exist_ok=True)
    os.makedirs(crops_dir, exist_ok=True)

    RANDOM_CLASSES = [
        {"type": "Car / Hatchback", "w": 46, "h": 72, "default_color": (35, 140, 220)},
        {"type": "Auto-Rickshaw (3-Wheeler)", "w": 38, "h": 52, "default_color": (30, 200, 230)},
        {"type": "Two-Wheeler (Bike/Scooter)", "w": 22, "h": 46, "default_color": (30, 30, 30)},
        {"type": "Commercial Mini-Truck", "w": 56, "h": 82, "default_color": (230, 220, 210)},
        {"type": "SUV / MUV", "w": 54, "h": 88, "default_color": (160, 160, 160)},
        {"type": "City Bus / Heavy Vehicle", "w": 65, "h": 125, "default_color": (40, 160, 60)},
        {"type": "Car / Hatchback", "w": 46, "h": 74, "default_color": (220, 220, 220)},
        {"type": "Two-Wheeler (Bike/Scooter)", "w": 22, "h": 46, "default_color": (80, 20, 20)}
    ]

    COLOR_PALETTE = [
        (40, 40, 220),    # Red / Crimson
        (225, 225, 225),  # Pure White
        (20, 180, 220),   # Golden / Yellow
        (180, 80, 30),    # Cobalt Blue
        (30, 140, 50),    # Forest Green
        (160, 160, 165),  # Metallic Silver
        (35, 35, 38),     # Obsidian Black
        (90, 40, 120),    # Deep Plum
        (40, 120, 190)    # Amber Orange
    ]

    lane_x_map = {1: 180, 2: 380}
    cam_a_tracklets = []
    cam_b_tracklets = []

    frame_a = create_road_canvas(640, 360, "CAM-A", "Junction 4th Ave (Random Run)")
    frame_b = create_road_canvas(640, 360, "CAM-B", "Junction 5th Ave (Random Run)")

    base_time_a = 15.0
    num_vehicles = random.randint(6, 8)
    chosen_templates = random.sample(RANDOM_CLASSES, min(num_vehicles, len(RANDOM_CLASSES)))

    y_positions_a = [35, 75, 120, 165, 205, 245, 280, 140]
    random.shuffle(y_positions_a)

    for idx, tmpl in enumerate(chosen_templates):
        v_id = f"RND-{idx+1:02d}"
        body_bgr = random.choice(COLOR_PALETTE)
        roof_bgr = (
            max(0, body_bgr[0] - 25),
            max(0, body_bgr[1] - 25),
            max(0, body_bgr[2] - 25)
        )
        lane = (idx % 2) + 1
        cx = lane_x_map[lane]
        w, h = tmpl["w"], tmpl["h"]
        x = cx - w // 2
        y_a = y_positions_a[idx] % (360 - h - 10)

        # Draw on Camera A
        draw_realistic_vehicle(frame_a, x, y_a, w, h, body_bgr, roof_bgr, tmpl["type"])
        crop_a = frame_a[y_a:y_a+h, x:x+w].copy()
        feat_a = extract_vehicle_features(crop_a)

        t_entry_a = base_time_a + idx * 8.0
        t_exit_a = t_entry_a + 5.5

        t_a = VehicleTracklet(
            track_id=f"CAM-A-{v_id}",
            camera_id="CAM-A",
            initial_bbox=(x, y_a, w, h),
            frame_idx=int(t_entry_a * 30),
            timestamp_sec=t_entry_a,
            crop_img=crop_a,
            features=feat_a
        )
        t_a.last_timestamp = t_exit_a
        t_a.last_frame = int(t_exit_a * 30)
        t_a.bboxes.append((x, y_a + 20, w, h))
        t_a.is_completed = True
        cam_a_tracklets.append(t_a)

        # Decide if this vehicle reaches Camera B (80% chance) or diverts (20% negative control)
        reaches_b = (random.random() < 0.80) or (idx < 3)
        if reaches_b:
            speed_kmh = random.uniform(32.0, 68.0)
            transit_sec = 850.0 / (speed_kmh / 3.6)
            t_entry_b = t_exit_a + transit_sec
            t_exit_b = t_entry_b + 5.5

            y_b = (y_a + random.randint(-20, 20)) % (360 - h - 10)
            lane_b = random.choice([1, 2])
            cx_b = lane_x_map[lane_b]
            x_b = cx_b - w // 2

            # Lighting shift for Camera B
            body_shifted = tuple(min(255, max(0, int(c * 0.94 + random.randint(4, 14)))) for c in body_bgr)
            roof_shifted = tuple(min(255, max(0, int(c * 0.94 + random.randint(4, 14)))) for c in roof_bgr)

            draw_realistic_vehicle(frame_b, x_b, y_b, w, h, body_shifted, roof_shifted, tmpl["type"])
            crop_b = frame_b[y_b:y_b+h, x_b:x_b+w].copy()
            feat_b = extract_vehicle_features(crop_b)

            t_b = VehicleTracklet(
                track_id=f"CAM-B-{v_id}",
                camera_id="CAM-B",
                initial_bbox=(x_b, y_b, w, h),
                frame_idx=int(t_entry_b * 30),
                timestamp_sec=t_entry_b,
                crop_img=crop_b,
                features=feat_b
            )
            t_b.last_timestamp = t_exit_b
            t_b.last_frame = int(t_exit_b * 30)
            t_b.bboxes.append((x_b, y_b + 20, w, h))
            t_b.is_completed = True
            cam_b_tracklets.append(t_b)

    # Save overview frames
    cam_a_path = os.path.join(cam_a_dir, "overview.jpg")
    cam_b_path = os.path.join(cam_b_dir, "overview.jpg")
    cv2.imwrite(cam_a_path, frame_a)
    cv2.imwrite(cam_b_path, frame_b)

    return {
        "cam_a_path": cam_a_path,
        "cam_b_path": cam_b_path,
        "cam_a_tracklets": cam_a_tracklets,
        "cam_b_tracklets": cam_b_tracklets
    }
