"""
Live Video Streamer Module
Generates real-time continuous video frames for Camera A and Camera B
demonstrating vehicle movement across non-overlapping surveillance corridors.
Serves native multipart/x-mixed-replace MJPEG video streams.
"""

import time
import cv2
import numpy as np
from data.sample_generator import create_road_canvas, draw_realistic_vehicle, DEMO_VEHICLES


def render_animated_camera_frame(camera_id="cam_a", step=0):
    """
    Renders a dynamic CCTV video frame with moving vehicles and tracking HUD.
    camera_id: 'cam_a' or 'cam_b'
    step: frame index for motion calculation
    """
    is_cam_a = "a" in camera_id.lower()
    cam_label = "CAMERA 01 (Junction 4th Ave Entry)" if is_cam_a else "CAMERA 02 (Junction 5th Ave Exit - 850m)"
    location = "North Approach" if is_cam_a else "South Exit (+850m)"

    w, h = 640, 360
    canvas = create_road_canvas(w, h, "CAM-A" if is_cam_a else "CAM-B", location)

    lane_x_map = {1: 180, 2: 380}
    cycle_length = 240  # 8-second smooth looping cycle at 30 fps

    # Filter vehicles relevant to this camera
    active_vehicles = []
    for v in DEMO_VEHICLES:
        lane_key = "lane_a" if is_cam_a else "lane_b"
        lane = v[lane_key]
        if lane == 0:
            continue  # Does not pass through this camera

        # Base speed in pixels per frame
        v_type = v["type"].lower()
        if "two-wheeler" in v_type:
            speed = 3.6  # Fast filtering bike
        elif "bus" in v_type:
            speed = 2.0  # Slower heavy transit bus
        elif "auto" in v_type:
            speed = 2.6
        else:
            speed = 3.0  # Standard cars

        # Phase offset between vehicles
        veh_num = int(v["id"].split("-")[1])
        base_offset = (veh_num * 38)

        # Travel delay between Camera A and Camera B (temporal gap of non-overlapping corridor)
        time_delay_frames = 65 if not is_cam_a else 0

        # Current vehicle y coordinate
        effective_step = (step - time_delay_frames + base_offset) % cycle_length
        y_pos = int(-100 + effective_step * speed)

        # Only draw if on screen
        if -80 <= y_pos <= (h + 40):
            cx = lane_x_map[lane]
            vw, vh = v["w"], v["h"]
            x_pos = cx - vw // 2

            # Camera B lighting shift
            body_color = v["body_bgr"]
            roof_color = v["roof_bgr"]
            if not is_cam_a:
                body_color = tuple(min(255, max(0, int(c * 0.94 + 10))) for c in body_color)
                roof_color = tuple(min(255, max(0, int(c * 0.94 + 10))) for c in roof_color)

            draw_realistic_vehicle(canvas, x_pos, y_pos, vw, vh, body_color, roof_color, v["type"])

            # Engineering Bounding Box & HUD Tag
            box_col = (255, 180, 40) if is_cam_a else (50, 210, 255)
            cv2.rectangle(canvas, (x_pos, y_pos), (x_pos + vw, y_pos + vh), box_col, 2)

            # Corner reticles on the bounding box
            r_len = 6
            cv2.line(canvas, (x_pos, y_pos), (x_pos + r_len, y_pos), (255, 255, 255), 2)
            cv2.line(canvas, (x_pos, y_pos), (x_pos, y_pos + r_len), (255, 255, 255), 2)
            cv2.line(canvas, (x_pos + vw, y_pos + vh), (x_pos + vw - r_len, y_pos + vh), (255, 255, 255), 2)
            cv2.line(canvas, (x_pos + vw, y_pos + vh), (x_pos + vw, y_pos + vh - r_len), (255, 255, 255), 2)

            # Label tag
            t_id = f"{'CAM-A' if is_cam_a else 'CAM-B'}-{v['id']}"
            short_type = v['type'].split(' ')[0]
            label = f"[{t_id}] {short_type}"
            (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)

            cv2.rectangle(canvas, (x_pos, y_pos - lh - 6), (x_pos + lw + 6, y_pos), (10, 16, 28), -1)
            cv2.rectangle(canvas, (x_pos, y_pos - lh - 6), (x_pos + lw + 6, y_pos), box_col, 1)
            cv2.putText(canvas, label, (x_pos + 3, y_pos - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, cv2.LINE_AA)

    # Frame HUD Watermark Bar
    now_ms = int(time.time() * 1000) % 1000
    sec_str = time.strftime("%H:%M:%S")
    cv2.rectangle(canvas, (0, h - 22), (w, h), (10, 15, 25), -1)
    cv2.putText(
        canvas,
        f"{cam_label} | UTC {sec_str}.{now_ms:03d} | LIVE RTSP FEED 30.0 FPS | RES: 640x360",
        (10, h - 7),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.38,
        (160, 190, 220),
        1,
        cv2.LINE_AA
    )

    return canvas


def generate_mjpeg_stream(camera_id="cam_a"):
    """
    Generator yielding multipart JPEG frames for real-time video streaming in HTML <img> tags.
    Runs continuously at ~25-30 frames per second.
    """
    step = 0
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 75]

    while True:
        frame = render_animated_camera_frame(camera_id, step)
        step = (step + 1) % 10000

        success, buffer = cv2.imencode(".jpg", frame, encode_params)
        if success:
            frame_bytes = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )

        # 33ms sleep for ~30 FPS
        time.sleep(0.033)
