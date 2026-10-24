"""
CityTrack AI - Root Application Launcher
Smart City Multi-Camera Vehicle Re-Identification Platform (SC-01)
Run this single file directly in VS Code by pressing 'F5' or 'Run Python File'.
"""

import os
import sys
import time
import webbrowser
import threading

# Add 'backend' to Python system path so all core modules resolve automatically
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app

def open_browser_delayed(url="http://127.0.0.1:5000", delay_sec=1.2):
    """Automatically opens the default browser once the server starts."""
    time.sleep(delay_sec)
    print(f"\n[INFO] Launching browser to: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[WARN] Could not automatically open browser: {e}")

def main():
    print("=" * 72)
    print(" CITYTRACK AI - MULTI-CAMERA VEHICLE RE-IDENTIFICATION PLATFORM")
    print(" Smart Cities Non-Plate Visual Appearance & Physics Gating Engine")
    print("=" * 72)
    print(f" [Root Directory]: {ROOT_DIR}")
    print(f" [Backend Path]:   {BACKEND_DIR}")
    print(" [Web Dashboard]:  http://127.0.0.1:5000")
    print("=" * 72)
    print("\nStarting local server on http://127.0.0.1:5000 ...")
    print("Press CTRL+C in this terminal anytime to stop the server.\n")

    # Start browser opener in background thread
    threading.Thread(target=open_browser_delayed, daemon=True).start()

    # Run the production-bundled Flask app
    app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    main()
