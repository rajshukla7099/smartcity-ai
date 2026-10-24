"""
MultiCam AI - Video Utilities & Synthetic Corridor Generator
Generates realistic non-overlapping CCTV corridor footage for testing:
- Camera A (Ingress Junction)
- Camera B (Egress Junction - 850m Downstream)
Includes road markings, Indian mixed traffic vehicles, and motion trajectories.
"""

import os
import cv2
import numpy as np

def generate_corridor_video(output_path, camera_label="CAMERA A (Ingress)", duration_sec=5.0, fps=25.0, is_night=False):
    """
    Synthesizes a realistic 640x360 MP4 surveillance video of Indian traffic.
    """
    width, height = 640, 360
    total_frames = int(duration_sec * fps)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Vehicle fleet definitions: (vtype, bgr_color, initial_x, initial_y, speed_vx, size_w, size_h)
    fleet = [
        {"type": "auto-rickshaw", "color": (30, 200, 230), "x": 50, "y": 140, "vx": 3.8, "w": 40, "h": 50},
        {"type": "car", "color": (40, 140, 220), "x": 160, "y": 210, "vx": 4.5, "w": 65, "h": 46},
        {"type": "motorcycle", "color": (30, 30, 30), "x": 30, "y": 120, "vx": 5.2, "w": 22, "h": 42},
        {"type": "truck", "color": (220, 210, 200), "x": 280, "y": 190, "vx": 3.5, "w": 55, "h": 52},
        {"type": "bus", "color": (180, 50, 40), "x": 400, "y": 160, "vx": 3.2, "w": 75, "h": 70},
        {"type": "car", "color": (160, 160, 160), "x": 10, "y": 260, "vx": 4.2, "w": 70, "h": 48},
    ]

    for frame_idx in range(total_frames):
        # Base asphalt road canvas
        if is_night:
            frame = np.full((height, width, 3), (25, 28, 32), dtype=np.uint8)
        else:
            frame = np.full((height, width, 3), (55, 60, 68), dtype=np.uint8)

        # Sidewalk & curbs
        cv2.rectangle(frame, (0, 0), (width, 80), (45, 50, 55) if not is_night else (20, 22, 25), -1)
        cv2.rectangle(frame, (0, 310), (width, height), (45, 50, 55) if not is_night else (20, 22, 25), -1)

        # Lane dividers (Dashed white lines)
        dash_offset = int((frame_idx * 4) % 40)
        for x in range(-40 + dash_offset, width + 40, 40):
            cv2.line(frame, (x, 150), (x + 20, 150), (220, 220, 220) if not is_night else (100, 100, 100), 2)
            cv2.line(frame, (x, 230), (x + 20, 230), (220, 220, 220) if not is_night else (100, 100, 100), 2)

        # Draw moving vehicles
        for v in fleet:
            vx_curr = int(v["x"] + v["vx"] * frame_idx) % (width + 100) - 50
            vy_curr = v["y"]
            bw = v["w"]
            bh = v["h"]
            color = v["color"]

            # Vehicle body
            cv2.rectangle(frame, (vx_curr, vy_curr), (vx_curr + bw, vy_curr + bh), color, -1)
            cv2.rectangle(frame, (vx_curr, vy_curr), (vx_curr + bw, vy_curr + bh), (20, 20, 20), 1)

            # Windshield / Roof stripe
            cv2.rectangle(frame, (vx_curr + int(bw * 0.2), vy_curr + int(bh * 0.2)),
                          (vx_curr + int(bw * 0.8), vy_curr + int(bh * 0.5)), (30, 40, 50), -1)

            # Wheels
            cv2.circle(frame, (vx_curr + int(bw * 0.25), vy_curr + bh - 2), 4, (15, 15, 15), -1)
            cv2.circle(frame, (vx_curr + int(bw * 0.75), vy_curr + bh - 2), 4, (15, 15, 15), -1)

            # Headlight beams in night mode
            if is_night:
                cv2.circle(frame, (vx_curr + bw, vy_curr + int(bh * 0.3)), 3, (200, 255, 255), -1)
                cv2.circle(frame, (vx_curr + bw, vy_curr + int(bh * 0.7)), 3, (200, 255, 255), -1)

        # Surveillance CCTV HUD overlay
        cv2.rectangle(frame, (0, 0), (width, 28), (10, 14, 20), -1)
        timestamp_str = f"14:15:{frame_idx/fps:04.1f} UTC"
        cv2.putText(frame, f"MULTICAM AI // {camera_label} // {timestamp_str}", (10, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 230, 255), 1, cv2.LINE_AA)

        out.write(frame)

    out.release()
    return output_path
