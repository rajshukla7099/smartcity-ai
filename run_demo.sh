#!/usr/bin/env bash
set -e

echo "========================================================"
echo "  CityTrack AI - Vehicle Re-Identification Engine"
echo "  Student Hackathon Engineering Prototype"
echo "========================================================"
echo ""

echo "[1/3] Verifying Python dependencies..."
python3 -c "import flask, cv2, numpy, PIL" >/dev/null 2>&1 || {
    echo "Installing missing Python dependencies..."
    pip install -r backend/requirements.txt
}

echo "[2/3] Verifying frontend bundle..."
if [ ! -f "frontend/dist/index.html" ]; then
    echo "Building frontend application..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

echo "[3/3] Running automated unit test suite..."
python3 backend/tests/test_reid_pipeline.py

echo ""
echo "========================================================"
echo "  Starting CityTrack AI Server on http://127.0.0.1:5000"
echo "  Open your browser to http://127.0.0.1:5000"
echo "========================================================"
echo ""

python3 backend/app.py
