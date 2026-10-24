"""
MultiCam AI — Smart City ITS Corridor Vehicle Re-Identification & Analytics
Main Entry Point & Server Runner (Track 05: Smart Cities | Problem SC-01)
DPDP Act 2023 & GDPR Compliant — Strictly Zero OCR / No License Plates
"""

import os
import sys
import time
import subprocess
import webbrowser

PORT = 8501
URL = f"http://localhost:{PORT}"

def check_dependencies():
    required = ["streamlit", "cv2", "pandas", "numpy", "plotly"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[!] Installing missing packages: {missing}")
        subprocess.run([sys.executable, "-m", "pip", "install", *missing], check=True)
    print("✓ Environment verified: All dependencies available.")

def ensure_sample_media():
    if not os.path.exists("demo_cam_a.mp4") or not os.path.exists("demo_cam_b.mp4"):
        print("[*] Generating corridor demo feeds (Camera A & Camera B)...")
        from src.utils.video_generator import generate_corridor_video
        generate_corridor_video("demo_cam_a.mp4", camera_label="CAMERA A (Ingress)", duration_sec=4.0)
        generate_corridor_video("demo_cam_b.mp4", camera_label="CAMERA B (Egress - 850m)", duration_sec=4.0)
        print("✓ Corridor demo feeds ready.")
    else:
        print("✓ Corridor demo feeds verified.")

def launch_dashboard():
    print("=" * 72)
    print(" 🏙️ MULTICAM AI — SMART CITY TRAFFIC RE-ID & FLOW ANALYTICS")
    print(" 🔒 Zero-OCR Appearance Matching · Privacy-Preserving DPDP 2023")
    print("=" * 72)
    print(f"\n[1] Local Server URL: {URL}")
    print("[2] Opening dashboard in your browser...")
    
    # Check if streamlit is already active on port
    import urllib.request
    already_running = False
    try:
        with urllib.request.urlopen(URL, timeout=1) as resp:
            if resp.status == 200:
                already_running = True
    except Exception:
        already_running = False

    if already_running:
        print(f"✓ Streamlit service already running on port {PORT}.")
        webbrowser.open(URL)
        print("✓ Opened live dashboard.")
        return

    # Launch Streamlit process
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.headless", "true",
        "--server.port", str(PORT),
        "--browser.serverAddress", "localhost",
        "--theme.base", "dark"
    ]
    
    proc = subprocess.Popen(cmd)
    time.sleep(2.0)
    webbrowser.open(URL)
    print(f"✓ MultiCam AI running at {URL} (PID: {proc.pid})")
    print("  Press Ctrl+C in this terminal to stop.")
    
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\nStopping MultiCam AI server...")
        proc.terminate()
        proc.wait()
        print("Server stopped cleanly.")

if __name__ == "__main__":
    check_dependencies()
    ensure_sample_media()
    launch_dashboard()
