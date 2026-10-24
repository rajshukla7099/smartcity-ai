"""
MultiCam AI - Master Runner for VS Code & Command Line
Launches the MultiCam AI Streamlit application and automatically opens the browser.
"""

import sys
import os
import time
import subprocess
import webbrowser

def main():
    print("=" * 80)
    print(" MULTICAM AI — MULTI-CAMERA VEHICLE RE-IDENTIFICATION & ANALYTICS")
    print(" Track 05: Smart Cities | Problem Code: SC-01")
    print(" Strictly Zero OCR / No License Plates · DPDP Act 2023 Compliant")
    print("=" * 80)
    print("\n[1/3] Verifying core modules...")

    try:
        import streamlit
        import cv2
        import pandas
        import plotly
        import numpy
        print("  ✓ All required libraries verified (Streamlit, OpenCV, Pandas, Plotly, NumPy).")
    except ImportError as e:
        print(f"  [!] Missing library: {e}. Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    print("\n[2/3] Checking demo corridor videos...")
    if not os.path.exists("demo_cam_a.mp4") or not os.path.exists("demo_cam_b.mp4"):
        from src.utils.video_generator import generate_corridor_video
        generate_corridor_video("demo_cam_a.mp4", camera_label="CAMERA A (Ingress)", duration_sec=4.0)
        generate_corridor_video("demo_cam_b.mp4", camera_label="CAMERA B (Egress - 850m)", duration_sec=4.0)
        print("  ✓ Corridor sample videos generated.")
    else:
        print("  ✓ Corridor sample videos ready.")

    print("\n[3/3] Starting MultiCam AI Streamlit Dashboard...")
    port = 8501
    url = f"http://localhost:{port}"
    print(f"  URL: {url}")
    print("=" * 80)
    print(f" Opening {url} in your browser in 2 seconds...\n")

    # Give Streamlit a moment to bind, then open browser
    def open_browser():
        time.sleep(2.0)
        webbrowser.open(url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Launch Streamlit process
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.port", str(port),
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    main()
