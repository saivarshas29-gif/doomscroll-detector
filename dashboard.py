import os
import sys
import sqlite3
import subprocess
import datetime
from flask import Flask, render_template, request, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "study_data.db")

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

# Global tracker for Doomscroll focus process
doomscroll_process = None


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Timetable table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            subject TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            room TEXT,
            instructor TEXT,
            color TEXT DEFAULT '#4F46E5'
        )
    """)

    # 2. Exams table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            exam_type TEXT NOT NULL,
            exam_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            venue TEXT,
            syllabus TEXT,
            notes TEXT
        )
    """)

    # 3. Tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT,
            due_date TEXT,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Pending',
            notes TEXT
        )
    """)

    # 4. Attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            attended INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            min_percentage REAL DEFAULT 75.0
        )
    """)

    # 5. GPA Courses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpa_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semester TEXT DEFAULT 'Semester 1',
            subject TEXT NOT NULL,
            credits REAL DEFAULT 3.0,
            grade_point REAL DEFAULT 9.0
        )
    """)

    # Check if empty, seed with initial sample data
    cursor.execute("SELECT COUNT(*) FROM timetable")
    if cursor.fetchone()[0] == 0:
        seed_sample_data(cursor)

    conn.commit()
    conn.close()


def seed_sample_data(cursor):
    # Sample Timetable
    sample_timetable = [
        ("Monday", "Data Structures & Algorithms", "09:00", "10:30", "Room 302", "Dr. Rao", "#3B82F6"),
        ("Monday", "Operating Systems", "11:00", "12:30", "Lab 2", "Prof. Sharma", "#10B981"),
        ("Tuesday", "Computer Networks", "09:30", "11:00", "Room 405", "Dr. Anita", "#8B5CF6"),
        ("Tuesday", "Database Management Systems", "13:30", "15:00", "Lab 4", "Prof. Verma", "#F59E0B"),
        ("Wednesday", "Data Structures & Algorithms", "09:00", "10:30", "Room 302", "Dr. Rao", "#3B82F6"),
        ("Wednesday", "Software Engineering", "11:00", "12:30", "Room 201", "Dr. Kapoor", "#EC4899"),
        ("Thursday", "Operating Systems", "10:00", "11:30", "Room 302", "Prof. Sharma", "#10B981"),
        ("Thursday", "Computer Networks", "14:00", "15:30", "Lab 1", "Dr. Anita", "#8B5CF6"),
        ("Friday", "Database Management Systems", "09:30", "11:00", "Room 405", "Prof. Verma", "#F59E0B"),
        ("Friday", "Machine Learning Fundamentals", "11:30", "13:00", "Seminar Hall", "Dr. Nair", "#06B6D4"),
        ("Saturday", "Project Lab & Seminar", "10:00", "13:00", "Innovation Lab", "Mentor Group", "#6366F1"),
    ]
    cursor.executemany("""
        INSERT INTO timetable (day, subject, start_time, end_time, room, instructor, color)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_timetable)

    # Sample Exams (Upcoming)
    today = datetime.date.today()
    sample_exams = [
        ("Data Structures & Algorithms", "Midterm Exam", (today + datetime.timedelta(days=4)).isoformat(), "10:00", "12:00", "Hall A", "Trees, Graphs, Dynamic Programming", "Bring ID card and scientific calculator"),
        ("Operating Systems", "Midterm Exam", (today + datetime.timedelta(days=9)).isoformat(), "14:00", "16:00", "Hall B", "Process scheduling, Deadlocks, Memory Management", "Formulas sheet will be provided"),
        ("Database Management Systems", "Practical Lab Exam", (today + datetime.timedelta(days=15)).isoformat(), "09:30", "12:30", "Lab 4", "SQL Queries, Normalization, Triggers", "Submit practical record book beforehand"),
        ("Computer Networks", "Final Semester Exam", (today + datetime.timedelta(days=28)).isoformat(), "10:00", "13:00", "Auditorium", "Entire Syllabus (Modules 1 - 5)", "Non-programmable calculator permitted"),
    ]
    cursor.executemany("""
        INSERT INTO exams (subject, exam_type, exam_date, start_time, end_time, venue, syllabus, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_exams)

    # Sample Tasks
    sample_tasks = [
        ("Submit DSA Assignment 3", "Data Structures & Algorithms", (today + datetime.timedelta(days=2)).isoformat(), "High", "Pending", "Implement AVL Tree and Dijkstra's algorithm in Python"),
        ("OS Memory Management Case Study", "Operating Systems", (today + datetime.timedelta(days=5)).isoformat(), "Medium", "In Progress", "Prepare 5-page report on Virtual Memory Paging"),
        ("DBMS Schema Design Project", "Database Management Systems", (today + datetime.timedelta(days=7)).isoformat(), "High", "Pending", "Finalize ER diagram and DDL scripts"),
        ("Review Computer Networks Unit 2", "Computer Networks", (today + datetime.timedelta(days=3)).isoformat(), "Low", "Completed", "Data Link layer framing and CRC parity checks"),
    ]
    cursor.executemany("""
        INSERT INTO tasks (title, subject, due_date, priority, status, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, sample_tasks)

    # Sample Attendance
    sample_attendance = [
        ("Data Structures & Algorithms", 24, 28, 75.0),
        ("Operating Systems", 22, 26, 75.0),
        ("Computer Networks", 19, 25, 75.0),
        ("Database Management Systems", 25, 27, 75.0),
        ("Software Engineering", 18, 20, 75.0),
    ]
    cursor.executemany("""
        INSERT INTO attendance (subject, attended, total, min_percentage)
        VALUES (?, ?, ?, ?)
    """, sample_attendance)

    # Sample GPA Courses
    sample_gpa = [
        ("Semester 5", "Data Structures & Algorithms", 4.0, 9.0),
        ("Semester 5", "Operating Systems", 4.0, 8.5),
        ("Semester 5", "Database Systems", 3.0, 9.5),
        ("Semester 5", "Computer Networks", 3.0, 8.0),
        ("Semester 5", "Software Engineering Lab", 2.0, 10.0),
    ]
    cursor.executemany("""
        INSERT INTO gpa_courses (semester, subject, credits, grade_point)
        VALUES (?, ?, ?, ?)
    """, sample_gpa)


@app.route("/")
def index():
    return render_template("index.html")


# ==========================================
# 📊 OVERVIEW & STATS API
# ==========================================
@app.route("/api/stats", methods=["GET"])
def get_stats():
    conn = get_db()
    cursor = conn.cursor()

    # Current Day of Week
    today_str = datetime.date.today().strftime("%A")
    today_iso = datetime.date.today().isoformat()

    # Today's classes count
    cursor.execute("SELECT COUNT(*) FROM timetable WHERE day = ?", (today_str,))
    today_classes_count = cursor.fetchone()[0]

    # Upcoming exams in next 14 days
    cursor.execute("""
        SELECT COUNT(*) FROM exams 
        WHERE exam_date >= ? AND exam_date <= date(?, '+14 days')
    """, (today_iso, today_iso))
    upcoming_exams_count = cursor.fetchone()[0]

    # Next immediate exam
    cursor.execute("""
        SELECT * FROM exams 
        WHERE exam_date >= ? 
        ORDER BY exam_date ASC, start_time ASC LIMIT 1
    """, (today_iso,))
    next_exam_row = cursor.fetchone()
    next_exam = dict(next_exam_row) if next_exam_row else None

    # Pending & In-progress tasks
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status != 'Completed'")
    pending_tasks_count = cursor.fetchone()[0]

    # Average Attendance Percentage
    cursor.execute("SELECT SUM(attended), SUM(total) FROM attendance")
    att_row = cursor.fetchone()
    total_attended = att_row[0] or 0
    total_classes = att_row[1] or 0
    avg_attendance = round((total_attended / total_classes * 100), 1) if total_classes > 0 else 0.0

    conn.close()

    return jsonify({
        "today_day": today_str,
        "today_classes_count": today_classes_count,
        "upcoming_exams_count": upcoming_exams_count,
        "next_exam": next_exam,
        "pending_tasks_count": pending_tasks_count,
        "avg_attendance": avg_attendance,
        "total_attended": total_attended,
        "total_classes": total_classes
    })


# ==========================================
# 📅 TIMETABLE API
# ==========================================
@app.route("/api/timetable", methods=["GET", "POST", "DELETE"])
def api_timetable():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "GET":
        day = request.args.get("day")
        if day:
            cursor.execute("SELECT * FROM timetable WHERE day = ? ORDER BY start_time ASC", (day,))
        else:
            cursor.execute("SELECT * FROM timetable ORDER BY CASE day "
                           "WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 "
                           "WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 ELSE 7 END, start_time ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return jsonify(rows)

    elif request.method == "POST":
        data = request.json
        cursor.execute("""
            INSERT INTO timetable (day, subject, start_time, end_time, room, instructor, color)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("day", "Monday"),
            data.get("subject", ""),
            data.get("start_time", "09:00"),
            data.get("end_time", "10:00"),
            data.get("room", ""),
            data.get("instructor", ""),
            data.get("color", "#4F46E5")
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"success": True, "id": new_id})

    elif request.method == "DELETE":
        item_id = request.args.get("id")
        if item_id:
            cursor.execute("DELETE FROM timetable WHERE id = ?", (item_id,))
            conn.commit()
        conn.close()
        return jsonify({"success": True})


# ==========================================
# 📝 EXAMS API
# ==========================================
@app.route("/api/exams", methods=["GET", "POST", "DELETE"])
def api_exams():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "GET":
        cursor.execute("SELECT * FROM exams ORDER BY exam_date ASC, start_time ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return jsonify(rows)

    elif request.method == "POST":
        data = request.json
        cursor.execute("""
            INSERT INTO exams (subject, exam_type, exam_date, start_time, end_time, venue, syllabus, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("subject", ""),
            data.get("exam_type", "Midterm"),
            data.get("exam_date", datetime.date.today().isoformat()),
            data.get("start_time", "10:00"),
            data.get("end_time", "12:00"),
            data.get("venue", ""),
            data.get("syllabus", ""),
            data.get("notes", "")
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"success": True, "id": new_id})

    elif request.method == "DELETE":
        item_id = request.args.get("id")
        if item_id:
            cursor.execute("DELETE FROM exams WHERE id = ?", (item_id,))
            conn.commit()
        conn.close()
        return jsonify({"success": True})


# ==========================================
# ✅ TASKS API
# ==========================================
@app.route("/api/tasks", methods=["GET", "POST", "PUT", "DELETE"])
def api_tasks():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "GET":
        status = request.args.get("status")
        if status and status != "All":
            cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY due_date ASC", (status,))
        else:
            cursor.execute("SELECT * FROM tasks ORDER BY CASE status WHEN 'Pending' THEN 1 WHEN 'In Progress' THEN 2 ELSE 3 END, due_date ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return jsonify(rows)

    elif request.method == "POST":
        data = request.json
        cursor.execute("""
            INSERT INTO tasks (title, subject, due_date, priority, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get("title", ""),
            data.get("subject", ""),
            data.get("due_date", datetime.date.today().isoformat()),
            data.get("priority", "Medium"),
            data.get("status", "Pending"),
            data.get("notes", "")
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"success": True, "id": new_id})

    elif request.method == "PUT":
        data = request.json
        task_id = data.get("id")
        if task_id:
            cursor.execute("""
                UPDATE tasks SET status = ?, priority = ?, title = ?, subject = ?, due_date = ?, notes = ?
                WHERE id = ?
            """, (
                data.get("status", "Pending"),
                data.get("priority", "Medium"),
                data.get("title"),
                data.get("subject"),
                data.get("due_date"),
                data.get("notes"),
                task_id
            ))
            conn.commit()
        conn.close()
        return jsonify({"success": True})

    elif request.method == "DELETE":
        item_id = request.args.get("id")
        if item_id:
            cursor.execute("DELETE FROM tasks WHERE id = ?", (item_id,))
            conn.commit()
        conn.close()
        return jsonify({"success": True})


# ==========================================
# 📈 ATTENDANCE API
# ==========================================
@app.route("/api/attendance", methods=["GET", "POST", "PUT", "DELETE"])
def api_attendance():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "GET":
        cursor.execute("SELECT * FROM attendance ORDER BY subject ASC")
        rows = []
        for r in cursor.fetchall():
            d = dict(r)
            attended = d["attended"]
            total = d["total"]
            min_p = d["min_percentage"]
            curr_p = round((attended / total * 100), 1) if total > 0 else 0.0
            d["percentage"] = curr_p

            # Calculate safe bunks or required classes
            if total == 0:
                d["status_text"] = "No classes recorded yet"
                d["can_bunk"] = 0
            elif curr_p >= min_p:
                # How many can bunk: (attended) / (total + x) >= min_p / 100
                # x <= (attended * 100 / min_p) - total
                max_total = int((attended * 100) / min_p)
                safe_bunks = max(0, max_total - total)
                d["can_bunk"] = safe_bunks
                d["status_text"] = f"Safe to bunk {safe_bunks} more class{'es' if safe_bunks != 1 else ''}"
            else:
                # How many must attend: (attended + y) / (total + y) >= min_p / 100
                # y * (1 - min_p/100) >= (min_p/100 * total) - attended
                req = int(round(((min_p / 100.0 * total) - attended) / (1 - min_p / 100.0) + 0.49))
                req = max(1, req)
                d["can_bunk"] = 0
                d["status_text"] = f"Must attend next {req} class{'es' if req != 1 else ''} consecutively"
            rows.append(d)
        conn.close()
        return jsonify(rows)

    elif request.method == "POST":
        data = request.json
        cursor.execute("""
            INSERT INTO attendance (subject, attended, total, min_percentage)
            VALUES (?, ?, ?, ?)
        """, (
            data.get("subject", ""),
            int(data.get("attended", 0)),
            int(data.get("total", 0)),
            float(data.get("min_percentage", 75.0))
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"success": True, "id": new_id})

    elif request.method == "PUT":
        data = request.json
        item_id = data.get("id")
        action = data.get("action")  # 'attend', 'miss', or 'update'

        if action == "attend":
            cursor.execute("UPDATE attendance SET attended = attended + 1, total = total + 1 WHERE id = ?", (item_id,))
        elif action == "miss":
            cursor.execute("UPDATE attendance SET total = total + 1 WHERE id = ?", (item_id,))
        else:
            cursor.execute("""
                UPDATE attendance SET subject = ?, attended = ?, total = ?, min_percentage = ?
                WHERE id = ?
            """, (
                data.get("subject"),
                int(data.get("attended", 0)),
                int(data.get("total", 0)),
                float(data.get("min_percentage", 75.0)),
                item_id
            ))
        conn.commit()
        conn.close()
        return jsonify({"success": True})

    elif request.method == "DELETE":
        item_id = request.args.get("id")
        if item_id:
            cursor.execute("DELETE FROM attendance WHERE id = ?", (item_id,))
            conn.commit()
        conn.close()
        return jsonify({"success": True})


# ==========================================
# 🎓 GPA & GRADE CALCULATOR API
# ==========================================
@app.route("/api/gpa", methods=["GET", "POST", "DELETE"])
def api_gpa():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "GET":
        cursor.execute("SELECT * FROM gpa_courses ORDER BY semester ASC, subject ASC")
        rows = [dict(r) for r in cursor.fetchall()]

        # Calculate GPA per semester and overall
        total_credits = sum(r["credits"] for r in rows)
        total_weighted_points = sum(r["credits"] * r["grade_point"] for r in rows)
        overall_gpa = round(total_weighted_points / total_credits, 2) if total_credits > 0 else 0.0

        conn.close()
        return jsonify({
            "courses": rows,
            "total_credits": total_credits,
            "overall_gpa": overall_gpa
        })

    elif request.method == "POST":
        data = request.json
        cursor.execute("""
            INSERT INTO gpa_courses (semester, subject, credits, grade_point)
            VALUES (?, ?, ?, ?)
        """, (
            data.get("semester", "Semester 1"),
            data.get("subject", ""),
            float(data.get("credits", 3.0)),
            float(data.get("grade_point", 9.0))
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"success": True, "id": new_id})

    elif request.method == "DELETE":
        item_id = request.args.get("id")
        if item_id:
            cursor.execute("DELETE FROM gpa_courses WHERE id = ?", (item_id,))
            conn.commit()
        conn.close()
        return jsonify({"success": True})


# ==========================================
# 🎯 DOOMSCROLL FOCUS MODE INTEGRATION API
# ==========================================
@app.route("/api/focus/status", methods=["GET"])
def focus_status():
    global doomscroll_process
    is_running = False
    if doomscroll_process is not None:
        if doomscroll_process.poll() is None:
            is_running = True
        else:
            doomscroll_process = None
    return jsonify({"running": is_running})


@app.route("/api/focus/start", methods=["POST"])
def focus_start():
    global doomscroll_process
    if doomscroll_process is not None and doomscroll_process.poll() is None:
        return jsonify({"success": True, "message": "Doomscroll detector is already running!"})

    doomscroll_script = os.path.join(BASE_DIR, "Doomscroll.py")
    python_executable = sys.executable

    try:
        # Launch Doomscroll.py as independent process
        doomscroll_process = subprocess.Popen(
            [python_executable, doomscroll_script],
            cwd=BASE_DIR
        )
        return jsonify({"success": True, "message": "Doomscroll Camera Shield started!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to start: {str(e)}"}), 500


@app.route("/api/focus/stop", methods=["POST"])
def focus_stop():
    global doomscroll_process
    if doomscroll_process is not None and doomscroll_process.poll() is None:
        doomscroll_process.terminate()
        doomscroll_process = None
        return jsonify({"success": True, "message": "Doomscroll detector stopped."})
    return jsonify({"success": True, "message": "Detector is not running."})


if __name__ == "__main__":
    init_db()
    print("\n" + "="*60)
    print("🚀 FocusSphere Study Dashboard is running at:")
    print("👉 http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, host="127.0.0.1", port=5000)

