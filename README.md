# WinSphere — Study Dashboard & Focus Shield 🎓📵

A modern, full-featured academic productivity hub built with **Flask**, **SQLite**, **Tailwind CSS**, and an integrated **AI Doomscroll Camera Shield** powered by **YOLOv8** & **OpenCV**.

---

## ✨ Features

### 1. 📅 Semester Timetable
- Track your weekly class and laboratory schedule from Monday to Saturday.
- Color-coded subject tags, room/hall numbers, instructor assignments, and class timings.
- Add and delete classes dynamically.

### 2. 📝 Exam & Test Tracker
- Track Midterm exams, Final semester exams, Lab practicals, and Unit tests.
- **Live Real-Time Countdown Clocks** (`3d 14h left`) with dynamic urgency color indicators.
- Track exam venues, syllabus topics, and special examination instructions.

### 3. ✅ Task & Assignment Manager
- Prioritized task manager with **High**, **Medium**, and **Low** priority badges.
- Track due dates and mark assignments complete with instant checkbox toggles.
- Filter tasks by status: *All*, *Pending*, *In Progress*, or *Completed*.

### 4. 🎯 Focus Chamber & Pomodoro Timer
- **Integrated Doomscroll Camera Shield**:
  - Launch or stop the AI webcam detector with a single click directly from the dashboard!
  - Detects phone pickups and tilted/slanting angles while studying and plays an alert chime after 1.5 seconds.
- **Pomodoro Timer**:
  - Standard intervals: 25 min Study, 5 min Short Break, 15 min Long Break.
  - Interactive timer controls with synthesized Web Audio chimes upon completion.
  - Session counter tracking your study streak.

### 5. 📈 Attendance & Bunk Calculator
- Subject-wise attendance progress bars with minimum target indicators (default: 75%).
- **Smart Bunk Predictor**:
  - Calculates exactly how many classes you can safely skip.
  - If below target: Calculates exactly how many consecutive classes you must attend to avoid detention.
  - Quick **+1 Attended** and **+1 Missed** buttons for 1-second daily logging.

### 6. 🎓 GPA & Target Grade Predictor
- Calculates your overall SGPA and CGPA weighted by course credit units.
- Evaluates academic standing (Distinction / Honors / First Class).
- Add semester courses with credit weights and grade points.

---

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run the Study Dashboard
```powershell
python dashboard.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

### 3. Run Standalone Doomscroll Detector (Optional)
```powershell
python Doomscroll.py
```
*Press `q` in the camera window to quit.*
