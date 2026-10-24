"""
MultiCam AI — Direct Public Cloudflare Tunnel Runner (Zero Password)
Creates an instant, direct public HTTPS link on trycloudflare.com.
Zero password required! Anyone can open it directly on their phone or laptop.
"""

import sys
import os
import time
import subprocess
import urllib.request
import webbrowser
import re

PORT = 8501
CLOUDFLARED_EXE = os.path.abspath("cloudflared.exe")

def ensure_streamlit_running():
    print("[1/2] Checking local MultiCam AI Streamlit server...")
    try:
        with urllib.request.urlopen(f"http://localhost:{PORT}", timeout=1) as resp:
            if resp.status == 200:
                print("  ✓ Local Streamlit dashboard is active on port 8501.")
                return None
    except Exception:
        pass

    print("  [*] Starting local Streamlit server in background...")
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.headless", "true",
        "--server.port", str(PORT),
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.5)
    print("  ✓ Local Streamlit server started.")
    return proc

def start_cloudflare_tunnel():
    print("\n[2/2] Launching Direct Public HTTPS Tunnel (Zero Password)...")
    print("=" * 75)

    if not os.path.exists(CLOUDFLARED_EXE):
        print("[!] Error: cloudflared.exe not found in directory.")
        return

    cmd = [CLOUDFLARED_EXE, "tunnel", "--url", f"http://localhost:{PORT}"]
    tunnel_proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    public_url = None
    for line in iter(tunnel_proc.stdout.readline, ""):
        line_str = line.strip()
        match = re.search(r"https://[a-zA-Z0-9\-\.]+\.trycloudflare\.com", line_str)
        if match:
            public_url = match.group(0)
            break

    if public_url:
        print("=" * 75)
        print(" 🎉 MULTICAM AI IS NOW LIVE GLOBALLY (ZERO PASSWORD REQUIRED)!")
        print(f" 🌐 DIRECT PUBLIC LINK: {public_url}")
        print("=" * 75)
        print("\n👉 Send this link to judges — they can open it immediately on their phones!")
        print("👉 Opening link in your browser now...\n")
        try:
            webbrowser.open(public_url)
        except Exception:
            pass

    try:
        tunnel_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping public tunnel...")
        tunnel_proc.terminate()
        tunnel_proc.wait()
        print("Tunnel stopped.")

if __name__ == "__main__":
    st_proc = ensure_streamlit_running()
    try:
        start_cloudflare_tunnel()
    finally:
        if st_proc is not None:
            st_proc.terminate()
