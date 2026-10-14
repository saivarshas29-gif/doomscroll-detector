# Doomscroll Detector 📵

A real-time AI computer vision assistant that alerts you whenever you pick up your phone and start doomscrolling while working.

Built with **YOLOv8**, **OpenCV**, and **Pygame**.

---

## ✨ Features

- **Real-Time Detection**: Uses YOLOv8 to track mobile phones in your camera feed.
- **Angle & Tilt Support**: Captures phones held obliquely, sideways, or at slanting angles.
- **Debounce Timer & Grace Period**: Ignores temporary hand shifts or momentary flickering without immediately resetting the alarm.
- **Audio & Visual Alerts**: Sounds a looping alarm and flashes warnings on-screen when a phone is held past the threshold (default: 1.5 seconds).
- **Graceful Fallbacks**: Works with `.mp3`, `.wav`, or Windows system beeps.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Set up virtual environment & install dependencies
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # On Windows PowerShell
pip install -r requirements.txt
```

### 3. Run the detector
```bash
python Doomscroll.py
```

*Press `q` on the camera window to quit.*
