# 🚦 Live Traffic Command Center & Vehicle Tracking Engine

A production-grade, full-stack computer vision application that processes video traffic feeds to detect, track, and analyze multi-class vehicular traffic patterns. This system integrates real-time object tracking algorithms with deep-learning vision models and presents actionable analytical telemetry inside a responsive web dashboard.

🚀 **Live Demo:** *(Add your deployment link here)*

---

# 🌟 Features

## 🎯 AI Vehicle Detection

* Real-time vehicle detection using **YOLO (You Only Look Once)** deep learning models.
* Detects multiple vehicle categories:

  * Car
  * Truck
  * Bus
  * Motorcycle
  * Auto Rickshaw

---

## 📍 Vehicle Tracking System

* Uses **Centroid Tracking Algorithm** for smooth object tracking.
* Prevents:

  * Bounding box flickering
  * Duplicate counting
  * Frame skipping issues

---

## ⚡ Performance Modes

### 🚀 Fast Processing Mode

* Processes video frames in background.
* Optimized for:

  * Faster inference
  * Low-latency counting
  * High-speed analytics

### 📺 Live Visualization Mode

* Displays:

  * Bounding boxes
  * Vehicle IDs
  * Tracking lines
  * Live detection overlays

---

## ✂️ Automatic Vehicle Crop Storage

* Captures cropped images of detected vehicles.
* Saves images automatically when vehicles cross counting boundary.
* Organized local storage system for audit purposes.

---

## 📊 Advanced Analytics Dashboard

Interactive analytics powered using **Plotly**.

### Includes:

* Vehicle count statistics
* Vehicle distribution pie charts
* Hourly traffic density graphs
* Congestion analysis
* Bar charts
* CSV export support

---

## 🗂️ Historical Log Management

* Searchable detection history
* Vehicle type filtering
* Timestamp-based logs
* Cropped image preview system

---

# 🛠️ Tech Stack

| Category           | Technology                 |
| ------------------ | -------------------------- |
| Frontend Dashboard | Streamlit                  |
| Deep Learning      | YOLO, Ultralytics, PyTorch |
| Tracking           | Centroid Tracking          |
| Data Processing    | Pandas, NumPy              |
| Visualization      | Plotly                     |
| Database           | SQLAlchemy                 |
| Backend Language   | Python                     |

---

# 📁 Project Structure

```text
Vehicle-Counting-at-Traffic-Signal/
│
├── data/
│   └── crops/                # Saved vehicle crop images
│
├── src/
│   ├── analytics/            # Analytics calculations
│   ├── models/               # YOLO detection models
│   └── tracking/             # Vehicle tracking algorithms
│
├── requirements.txt          # Python dependencies
├── streamlit_app.py          # Main Streamlit application
└── README.md
```

---

# 💻 Installation Guide

## 1️⃣ Clone Repository

```bash
git clone https://github.com/co-work-space/Vehicle-Counting-at-Traffic-Signal.git

cd Vehicle-Counting-at-Traffic-Signal
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv vehicle_env

vehicle_env\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv vehicle_env

source vehicle_env/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Application

```bash
streamlit run streamlit_app.py
```

---

# ⚙️ System Workflow

## Step 1

Upload traffic surveillance video.

## Step 2

YOLO model detects vehicles frame-by-frame.

## Step 3

Tracker assigns unique IDs to each vehicle.

## Step 4

Vehicles crossing counting line are:

* Counted
* Logged
* Cropped and saved

## Step 5

Analytics dashboard updates in real-time.

---

# 📏 Counting Logic

Vehicles are counted when they cross:

```python
frame_height * 0.75
```

This creates a virtual counting boundary near the lower section of frame.

---

# 📊 Analytics Included

* Total Vehicle Count
* Vehicle Type Distribution
* Peak Traffic Analysis
* Congestion Metrics
* Traffic Flow Visualization
* Historical Data Export

---

# 🚀 Performance Optimization

For maximum speed:

1. Disable **Live Video View**
2. Enable **Fast Mode**
3. Increase processing speed slider
4. Run on GPU-enabled system (recommended)

---

# 🧠 Future Enhancements

* Multi-camera integration
* License plate recognition
* Accident detection
* Traffic violation detection
* Cloud database integration
* Live CCTV streaming support
* AI-based congestion prediction







Generated based on your uploaded project details. 
