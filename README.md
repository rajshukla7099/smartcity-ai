# MultiCam AI 🚦
### Multi-Camera Vehicle Re-Identification & Traffic Flow Analytics

> **Smart City & Intelligent Transportation Systems (ITS) Platform**  
> *Non-overlapping multi-camera vehicle tracking, visual re-identification, and origin-destination flow analytics — without reading license plates or OCR.*

---

## 📋 1. Project Overview & Problem Statement

Municipalities and urban planners design roads and public transport using outdated, manual roadside surveys of where journeys begin and end. Using footage from multiple **non-overlapping CCTV traffic cameras**, MultiCam AI detects, tracks, and re-identifies vehicles across blind corridor segments to estimate traffic flows between them.

### Strict Non-OCR Requirement
- **License plate recognition or OCR is strictly prohibited.**
- Vehicles are matched solely by **privacy-preserving visual appearance features** (3-stripe spatial color histograms, aspect ratio, shape) fused with **spatio-temporal travel-time physics gating** ($v = \frac{d}{\Delta t} \times 3.6\text{ km/h}$).
- 100% compliant with India's **Digital Personal Data Protection (DPDP) Act 2023** and **GDPR**.

---

## 🛠️ 2. System Architecture & Tech Stack

```
   [Camera A: Ingress]                         [Camera B: Egress - 850m]
            │                                              │
            ▼                                              ▼
 ┌──────────────────────┐                       ┌──────────────────────┐
 │  Vehicle Detector    │                       │  Vehicle Detector    │
 │ (YOLOv8 / OpenCV MOG)│                       │ (YOLOv8 / OpenCV MOG)│
 └──────────┬───────────┘                       └──────────┬───────────┘
            │                                              │
            ▼                                              ▼
 ┌──────────────────────┐                       ┌──────────────────────┐
 │ Multi-Object Tracker │                       │ Multi-Object Tracker │
 │(IoU Kalman Tracklets)│                       │(IoU Kalman Tracklets)│
 └──────────┬───────────┘                       └──────────┬───────────┘
            │                                              │
            ▼                                              ▼
 ┌──────────────────────┐                       ┌──────────────────────┐
 │ Appearance Extractor │                       │ Appearance Extractor │
 │(3-Stripe HSV & 64d)  │                       │(3-Stripe HSV & 64d)  │
 └──────────┬───────────┘                       └──────────┬───────────┘
            │                                              │
            └──────────────────────┬───────────────────────┘
                                   │
                                   ▼
                 ┌───────────────────────────────────┐
                 │    Cross-Camera Re-ID Matcher     │
                 │   - Spatio-Temporal Speed Gating  │
                 │   - Cosine Visual Similarity      │
                 │   - Bipartite 1-to-1 Assignment   │
                 └─────────────────┬─────────────────┘
                                   │
                                   ▼
                 ┌───────────────────────────────────┐
                 │      MultiCam AI Dashboard        │
                 │   - Origin-Destination Matrix     │
                 │   - Travel Time Distribution      │
                 │   - Camera Failure Simulation     │
                 │   - Privacy k-Anonymity (k >= 10) │
                 └───────────────────────────────────┘
```

- **Frontend & UI**: Streamlit 1.35+ (Dark Theme, interactive Plotly visualizations)
- **Computer Vision**: OpenCV (cv2) 4.8+, Morphological Contours, CLAHE Night Enhancement
- **Detection**: Hybrid Ultralytics YOLOv8 & OpenCV Background Modeling
- **Analytics & Math**: NumPy, Pandas, Plotly Express
- **Privacy Framework**: $k$-anonymity suppression ($k \ge 10$)

---

## 📂 3. Project Structure

```
city ai/
├── app.py                      # MultiCam AI Streamlit web application
├── requirements.txt            # Python dependencies
├── README.md                   # Complete system documentation
├── demo_cam_a.mp4              # Sample Camera A traffic video
├── demo_cam_b.mp4              # Sample Camera B traffic video (+850m)
├── config/
│   └── corridor_config.json    # Camera corridor metadata & thresholds
├── src/
│   ├── detection/
│   │   └── detector.py         # Multi-class detector (Cars, Bikes, Buses, Trucks, Autos)
│   ├── tracking/
│   │   └── tracker.py          # Multi-object IoU Kalman tracker
│   ├── features/
│   │   └── appearance.py       # 3-Stripe HSV & 64d appearance embeddings (No OCR)
│   ├── matching/
│   │   └── reid_matcher.py     # Physics gating & bipartite Re-ID matcher
│   ├── analytics/
│   │   └── traffic_analytics.py# O-D matrix, flow rates, camera failure simulator
│   ├── privacy/
│   │   └── privacy_guard.py    # Group size >= 10 k-anonymity suppression
│   └── utils/
│       └── video_generator.py  # Synthetic corridor video generator & night mode
└── tests/
    └── test_multicam.py        # Automated unit & integration test suite
```

---

## 🚀 4. Quick Start & Demonstration Commands

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Automated Test Suite
```bash
python -m unittest tests/test_multicam.py
```
*(Verifies all 6 modules: detection, tracking, visual similarity, physics gating, analytics, and privacy export).*

### Step 3: Launch MultiCam AI Streamlit Dashboard
```bash
streamlit run app.py
```
*(The dashboard opens automatically in your browser at `http://localhost:8501`).*

---

## 🎯 5. System Demonstration & Workflow

1. **Tab 1 — Surveillance & Ingestion**:
   - Check the **"Use Built-in Corridor Demo Feeds"** box and click **"Run MultiCam AI Pipeline"**.
   - Show how the AI detects and classifies **Cars, Motorcycles, Buses, Commercial Trucks, and Auto-Rickshaws** with bounding boxes, tracking IDs, and dominant colors.
2. **Tab 2 — Multi-Camera Re-ID**:
   - Show the side-by-side vehicle visual match comparisons.
   - Explain the **3-Stripe Spatial Appearance** (Roof 30%, Body 45%, Chassis 25%) and the **Physical Travel-Time Window** ($\Delta t = 55\text{s}$, $55.2\text{ km/h}$).
   - Click **"Accept"** or **"Reject"** to demonstrate Human-in-the-Loop review.
3. **Tab 3 — Traffic Flow & O-D Matrix**:
   - Present the Origin-Destination (O-D) matrix between Junction 4th Ave and Junction 5th Ave.
   - Show the Indian mixed traffic modal split pie chart and travel time histogram.
4. **Tab 4 — Camera Failure Simulation**:
   - Select **"Camera B (Downstream Exit)"** and click **"Simulate Camera Failure"**.
   - Show the Bayesian survival flow projection estimating corridor volume under sensor outage with error bounds.
5. **Tab 5 — Privacy-Safe Export**:
   - Show how cohorts smaller than 10 are suppressed ($< 10$) to comply with $k$-anonymity.
   - Click **"Download Privacy-Compliant CSV Report"**.
