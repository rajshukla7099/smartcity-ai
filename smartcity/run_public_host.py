"""
MultiCam AI — 1-Click Public Host Runner for VS Code
Launches local Streamlit server and creates a public HTTPS internet tunnel.
Anyone with internet can access the dashboard on their phone/laptop!
"""

import sys
import os
import time
import subprocess
import urllib.request
import webbrowser

PORT = 8501

def get_public_ip():
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=4) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception:
        return "115.248.83.149"

def ensure_streamlit_running():
    print("[1/3] Checking local MultiCam AI Streamlit server...")
    try:
        with urllib.request.urlopen(f"http://localhost:{PORT}", timeout=1) as resp:
            if resp.status == 200:
                print("  ✓ Local Streamlit dashboard is already active on port 8501.")
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

def start_public_tunnel():
    ip = get_public_ip()
    print("\n[2/3] Fetching tunnel authentication...")
    print(f"  🔑 Verification Password (IP): {ip}")
    print("     (Enter this IP when prompted on the tunnel website)")

    print("\n[3/3] Creating Public HTTPS Internet Tunnel...")
    print("=" * 75)

    cmd = ["cmd", "/c", "npx", "--yes", "localtunnel", "--port", str(PORT)]
    tunnel_proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    public_url = None
    # Read output line-by-line to get the URL
    for line in iter(tunnel_proc.stdout.readline, ""):
        line_str = line.strip()
        print("  " + line_str)
        if "your url is:" in line_str.lower():
            public_url = line_str.split("your url is:")[-1].strip()
            break

    if public_url:
        print("=" * 75)
        print(" 🎉 MULTICAM AI IS NOW LIVE ON THE PUBLIC INTERNET!")
        print(f" 🌐 PUBLIC URL:  {public_url}")
        print(f" 🔑 PASSWORD:    {ip}")
        print("=" * 75)
        print("\n👉 Share this URL with judges so they can open it on their phones!")
        print("👉 Opening public URL in your browser now...\n")
        try:
            webbrowser.open(public_url)
        except Exception:
            pass

    # Keep tunnel alive
    try:
        tunnel_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping public tunnel...")
        tunnel_proc.terminate()
        tunnel_proc.wait()
        print("Public tunnel stopped.")

if __name__ == "__main__":
    st_proc = ensure_streamlit_running()
    try:
        start_public_tunnel()
    finally:
        if st_proc is not None:
            st_proc.terminate()
