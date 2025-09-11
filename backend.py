# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import mysql.connector
# import random
# from collections import defaultdict

# app = Flask(__name__)
# CORS(app)

# # -------------------------------
# # MySQL Connection Helper
# # -------------------------------
# def get_db_connection():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="sharma346",  # change if needed
#         database="timetable_db"
#     )

# # -------------------------------
# # Save Payload into MySQL
# # -------------------------------
# def save_to_database(data):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Clear old data (overwrite mode)
#     cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
#     cursor.execute("TRUNCATE TABLE faculty_subjects")
#     cursor.execute("TRUNCATE TABLE faculties")
#     cursor.execute("TRUNCATE TABLE departments")
#     cursor.execute("TRUNCATE TABLE labs")
#     cursor.execute("TRUNCATE TABLE lecture_rooms")
#     cursor.execute("TRUNCATE TABLE practicals")
#     cursor.execute("TRUNCATE TABLE subjects")
#     cursor.execute("TRUNCATE TABLE branches")
#     cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

#     # Insert Branches, Subjects, Practicals
#     for branch in data.get("branches", []):
#         cursor.execute(
#             """
#             INSERT INTO branches (name, total_students, class_hours_per_day, period_duration)
#             VALUES (%s, %s, %s, %s)
#             """,
#             (branch["name"], branch["totalStudents"], branch["classHoursPerDay"], branch["periodDuration"])
#         )
#         branch_id = cursor.lastrowid

#         for subj in branch.get("subjects", []):
#             cursor.execute(
#                 "INSERT INTO subjects (branch_id, subject_name) VALUES (%s, %s)",
#                 (branch_id, subj)
#             )

#         for prac in branch.get("practicals", []):
#             cursor.execute(
#                 "INSERT INTO practicals (branch_id, name, classes_per_week) VALUES (%s, %s, %s)",
#                 (branch_id, prac["name"], prac["classesPerWeek"])
#             )

#     # Lecture Rooms
#     lecture_rooms = data.get("lectureRooms", {})
#     if lecture_rooms:
#         cursor.execute(
#             "INSERT INTO lecture_rooms (total_rooms, max_capacity) VALUES (%s, %s)",
#             (lecture_rooms['totalRooms'], lecture_rooms['maxCapacity'])
#         )

#     # Labs
#     for lab in data.get("labs", []):
#         cursor.execute(
#             "INSERT INTO labs (type, num_labs, max_capacity) VALUES (%s, %s, %s)",
#             (lab['type'], lab['numLabs'], lab['maxCapacity'])
#         )

#     # Departments & Faculties
#     for dept in data.get("departments", []):
#         cursor.execute("INSERT INTO departments (name) VALUES (%s)", (dept["name"],))
#         dept_id = cursor.lastrowid

#         for fac in dept.get("faculties", []):
#             cursor.execute(
#                 "INSERT INTO faculties (department_id, name) VALUES (%s, %s)",
#                 (dept_id, fac["name"])
#             )
#             faculty_id = cursor.lastrowid

#             for subj in fac.get("assignedSubjects", []):
#                 cursor.execute(
#                     "INSERT INTO faculty_subjects (faculty_id, subject_name) VALUES (%s, %s)",
#                     (faculty_id, subj)
#                 )

#     conn.commit()
#     cursor.close()
#     conn.close()

# # -------------------------------
# # Fetch Data
# # -------------------------------
# def fetch_data():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("SELECT * FROM branches")
#     branches = cursor.fetchall()

#     cursor.execute("SELECT * FROM subjects")
#     subjects = cursor.fetchall()

#     cursor.execute("SELECT * FROM practicals")
#     practicals = cursor.fetchall()

#     cursor.execute("SELECT * FROM faculties")
#     faculties = cursor.fetchall()

#     cursor.execute("SELECT * FROM faculty_subjects")
#     faculty_subjects = cursor.fetchall()

#     cursor.execute("SELECT * FROM departments")
#     departments = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     return branches, subjects, practicals, faculties, faculty_subjects, departments

# # -------------------------------
# # Timetable Generator
# # -------------------------------
# def generate_timetable():
#     branches, subjects, practicals, faculties, faculty_subjects, departments = fetch_data()

#     working_days = 5  # Mon–Fri

#     # Build faculty map
#     faculty_map = {}
#     for fs in faculty_subjects:
#         faculty_map.setdefault(fs["subject_name"].strip().lower(), []).append(fs["faculty_id"])

#     faculty_workload = {f["name"]: 0 for f in faculties}
#     dept_workload = {d["name"]: 0 for d in departments}
#     subject_faculty_map = defaultdict(set)

#     timetable = {}

#     for branch in branches:
#         branch_id = branch["id"]
#         branch_name = branch["name"]
#         students = branch["total_students"]
#         hours_per_day = branch["class_hours_per_day"]
#         period_duration = branch["period_duration"]

#         periods_per_day = hours_per_day // period_duration
#         total_slots = working_days * periods_per_day

#         branch_subjects = [s for s in subjects if s["branch_id"] == branch_id]
#         branch_practicals = [p for p in practicals if p["branch_id"] == branch_id]

#         # -----------------------
#         # Adjust session counts
#         # -----------------------
#         sessions = []
#         if branch_subjects:
#             per_subject = max(1, total_slots // len(branch_subjects))  # distribute evenly
#             for subj in branch_subjects:
#                 for _ in range(per_subject):
#                     sessions.append({"subject": subj["subject_name"], "type": "lecture"})

#         for prac in branch_practicals:
#             for _ in range(prac["classes_per_week"]):
#                 sessions.append({"subject": prac["name"], "type": "practical"})

#         random.shuffle(sessions)

#         # Initialize timetable
#         timetable[branch_name] = {
#             day: {"Shift 1": [], "Shift 2": []} for day in range(working_days)
#         }

#         day_index = 0
#         for session in sessions:
#             subj = session["subject"].strip()
#             subj_key = subj.lower()

#             # Faculty assignment (with debug log)
#             if subj_key not in faculty_map:
#                 print(f"⚠️ No faculty found for subject: {subj}")
#                 fac_id = None
#             else:
#                 fac_id = random.choice(faculty_map[subj_key])

#             fac_name = next((f["name"] for f in faculties if f["id"] == fac_id), "Unassigned")

#             # Track faculty workload
#             if fac_name != "Unassigned":
#                 faculty_workload[fac_name] += 1
#                 subject_faculty_map[subj].add(fac_name)
#                 dept_id = next((f["department_id"] for f in faculties if f["id"] == fac_id), None)
#                 if dept_id:
#                     dept_name = next((d["name"] for d in departments if d["id"] == dept_id), None)
#                     if dept_name:
#                         dept_workload[dept_name] += 1

#             # Place session in timetable
#             day = day_index % working_days
#             shifts = timetable[branch_name][day]

#             if students > 60:  # split into 2 shifts if needed
#                 if len(shifts["Shift 1"]) < periods_per_day and len(shifts["Shift 2"]) < periods_per_day:
#                     shifts["Shift 1"].append((subj, fac_name, "Lecture Room 1"))
#                     shifts["Shift 2"].append((subj, fac_name, "Lecture Room 2"))
#                 else:
#                     if len(shifts["Shift 1"]) < periods_per_day:
#                         shifts["Shift 1"].append((subj, fac_name, "Lecture Room 1"))
#             else:
#                 if len(shifts["Shift 1"]) < periods_per_day:
#                     shifts["Shift 1"].append((subj, fac_name, "Lecture Room 1"))

#             day_index += 1

#         # -----------------------
#         # Fill empty slots with FREE
#         # -----------------------
#         for day in range(working_days):
#             for shift in ["Shift 1", "Shift 2"]:
#                 while len(timetable[branch_name][day][shift]) < periods_per_day:
#                     timetable[branch_name][day][shift].append(("FREE", "-", "-"))

#     return timetable, faculty_workload, subject_faculty_map, dept_workload

# # -------------------------------
# # Print Timetable
# # -------------------------------
# def print_timetable(timetable, faculty_workload, subject_faculty_map, dept_workload):
#     days = ["Mon", "Tue", "Wed", "Thu", "Fri"]

#     for branch, schedule in timetable.items():
#         print(f"\n=== Timetable for {branch} ===")
#         for d, shifts in schedule.items():
#             print(f"\n{days[d]}:")
#             for shift, slots in shifts.items():
#                 print(f"  {shift}:")
#                 for period, cls in enumerate(slots, 1):
#                     subject, faculty, room = cls
#                     print(f"    Period {period}: {subject} ({room}) by {faculty}")

#     print("\n=== Faculty Workload ===")
#     for fac, load in faculty_workload.items():
#         print(f"{fac}: {load} classes")

#     print("\n=== Subject-Faculty Mapping ===")
#     for subj, facs in subject_faculty_map.items():
#         print(f"{subj} → {', '.join(facs)}")

#     print("\n=== Department Workload ===")
#     for dept, load in dept_workload.items():
#         print(f"{dept}: {load} classes")

# # -------------------------------
# # Flask Route
# # -------------------------------
# @app.route('/generate-timetable', methods=['POST'])
# def generate_timetable_route():
#     data = request.get_json()
#     print("Received data:", data)

#     save_to_database(data)
#     timetable, faculty_workload, subject_faculty_map, dept_workload = generate_timetable()

#     # Debug print
#     print_timetable(timetable, faculty_workload, subject_faculty_map, dept_workload)

#     return jsonify({
#         "timetable": timetable,
#         "facultyWorkload": faculty_workload,
#         "subjectFacultyMap": {k: list(v) for k, v in subject_faculty_map.items()},
#         "departmentWorkload": dept_workload
#     })

# import json

# # Save selected timetable to DB
# @app.route('/save-timetable', methods=['POST'])
# def save_timetable():
#     data = request.get_json()
#     timetable = data.get("timetable")

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Clear old final timetable
#     cursor.execute("TRUNCATE TABLE final_timetable")

#     # Save new one (as JSON)
#     cursor.execute("INSERT INTO final_timetable (data) VALUES (%s)", (json.dumps(timetable),))

#     conn.commit()
#     cursor.close()
#     conn.close()

#     return jsonify({"message": "Timetable saved successfully"})


# # Fetch saved timetable
# @app.route('/get-saved-timetable', methods=['GET'])
# def get_saved_timetable():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("SELECT data FROM final_timetable LIMIT 1")
#     row = cursor.fetchone()

#     cursor.close()
#     conn.close()

#     if row:
#         return jsonify({"timetable": json.loads(row["data"])})
#     return jsonify({"timetable": None})

# # -------------------------------
# # Run Flask App
# # -------------------------------
# if __name__ == "__main__":
#     app.run(debug=True, port=5000)

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import random
from collections import defaultdict
import json

app = Flask(__name__)
CORS(app)

# -------------------------------
# MySQL Connection Helper
# -------------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sharma346",  # change if needed
        database="timetable_db"
    )

# -------------------------------
# Save Payload into MySQL
# -------------------------------
def save_to_database(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear old data (overwrite mode)
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("TRUNCATE TABLE faculty_subjects")
    cursor.execute("TRUNCATE TABLE faculties")
    cursor.execute("TRUNCATE TABLE departments")
    cursor.execute("TRUNCATE TABLE labs")
    cursor.execute("TRUNCATE TABLE lecture_rooms")
    cursor.execute("TRUNCATE TABLE practicals")
    cursor.execute("TRUNCATE TABLE subjects")
    cursor.execute("TRUNCATE TABLE branches")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    # Insert Branches, Subjects, Practicals
    for branch in data.get("branches", []):
        cursor.execute(
            """
            INSERT INTO branches (name, total_students, class_hours_per_day, period_duration)
            VALUES (%s, %s, %s, %s)
            """,
            (branch["name"], branch["totalStudents"], branch["classHoursPerDay"], branch["periodDuration"])
        )
        branch_id = cursor.lastrowid

        for subj in branch.get("subjects", []):
            cursor.execute(
                "INSERT INTO subjects (branch_id, subject_name) VALUES (%s, %s)",
                (branch_id, subj)
            )

        for prac in branch.get("practicals", []):
            cursor.execute(
                "INSERT INTO practicals (branch_id, name, classes_per_week) VALUES (%s, %s, %s)",
                (branch_id, prac["name"], prac["classesPerWeek"])
            )

    # Lecture Rooms
    lecture_rooms = data.get("lectureRooms", {})
    if lecture_rooms:
        cursor.execute(
            "INSERT INTO lecture_rooms (total_rooms, max_capacity) VALUES (%s, %s)",
            (lecture_rooms['totalRooms'], lecture_rooms['maxCapacity'])
        )

    # Labs
    for lab in data.get("labs", []):
        cursor.execute(
            "INSERT INTO labs (type, num_labs, max_capacity) VALUES (%s, %s, %s)",
            (lab['type'], lab['numLabs'], lab['maxCapacity'])
        )

    # Departments & Faculties
    for dept in data.get("departments", []):
        cursor.execute("INSERT INTO departments (name) VALUES (%s)", (dept["name"],))
        dept_id = cursor.lastrowid

        for fac in dept.get("faculties", []):
            cursor.execute(
                "INSERT INTO faculties (department_id, name) VALUES (%s, %s)",
                (dept_id, fac["name"])
            )
            faculty_id = cursor.lastrowid

            for subj in fac.get("assignedSubjects", []):
                cursor.execute(
                    "INSERT INTO faculty_subjects (faculty_id, subject_name) VALUES (%s, %s)",
                    (faculty_id, subj)
                )

    conn.commit()
    cursor.close()
    conn.close()

# -------------------------------
# Fetch Data
# -------------------------------
def fetch_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM branches")
    branches = cursor.fetchall()

    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()

    cursor.execute("SELECT * FROM practicals")
    practicals = cursor.fetchall()

    cursor.execute("SELECT * FROM faculties")
    faculties = cursor.fetchall()

    cursor.execute("SELECT * FROM faculty_subjects")
    faculty_subjects = cursor.fetchall()

    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()

    cursor.close()
    conn.close()

    return branches, subjects, practicals, faculties, faculty_subjects, departments

# -------------------------------
# Timetable Generator
# -------------------------------
def generate_timetable(max_lectures_per_faculty=10):
    branches, subjects, practicals, faculties, faculty_subjects, departments = fetch_data()
    working_days = 5  # Mon–Fri

    # Faculty lookup
    faculty_map = {}
    for fs in faculty_subjects:
        faculty_map.setdefault(fs["subject_name"].strip().lower(), []).append(fs["faculty_id"])

    # Workload tracking
    faculty_workload = {f["id"]: 0 for f in faculties}
    faculty_limits = {f["id"]: max_lectures_per_faculty for f in faculties}
    id_to_name = {f["id"]: f["name"] for f in faculties}

    dept_workload = {d["name"]: 0 for d in departments}
    subject_faculty_map = defaultdict(set)
    timetable = {}

    for branch in branches:
        branch_id = branch["id"]
        branch_name = branch["name"]
        students = branch["total_students"]
        hours_per_day = branch["class_hours_per_day"]
        period_duration = branch["period_duration"]

        periods_per_day = hours_per_day // period_duration
        total_slots = working_days * periods_per_day

        branch_subjects = [s for s in subjects if s["branch_id"] == branch_id]
        branch_practicals = [p for p in practicals if p["branch_id"] == branch_id]

        # Sessions
        sessions = []
        if branch_subjects:
            per_subject = max(1, total_slots // len(branch_subjects))
            for subj in branch_subjects:
                for _ in range(per_subject):
                    sessions.append({"subject": subj["subject_name"], "type": "lecture"})
        for prac in branch_practicals:
            for _ in range(prac["classes_per_week"]):
                sessions.append({"subject": prac["name"], "type": "practical"})

        random.shuffle(sessions)

        timetable[branch_name] = {day: {"Shift 1": [], "Shift 2": []} for day in range(working_days)}

        day_index = 0
        for session in sessions:
            subj = session["subject"].strip()
            subj_key = subj.lower()

            fac_id, fac_name = None, "Unassigned"
            if subj_key in faculty_map:
                available_faculties = [
                    f_id for f_id in faculty_map[subj_key]
                    if faculty_workload[f_id] < faculty_limits[f_id]
                ]
                if available_faculties:
                    fac_id = random.choice(available_faculties)
                    fac_name = id_to_name.get(fac_id, "Unassigned")

            # Update workloads
            if fac_id:
                faculty_workload[fac_id] += 1
                subject_faculty_map[subj].add(fac_name)
                dept_id = next((f["department_id"] for f in faculties if f["id"] == fac_id), None)
                if dept_id:
                    dept_name = next((d["name"] for d in departments if d["id"] == dept_id), None)
                    if dept_name:
                        dept_workload[dept_name] += 1

            # Assign to timetable
            day = day_index % working_days
            shifts = timetable[branch_name][day]

            if students > 60:
                if len(shifts["Shift 1"]) < periods_per_day and len(shifts["Shift 2"]) < periods_per_day:
                    shifts["Shift 1"].append((subj, fac_name, "Lecture Room 1"))
                    shifts["Shift 2"].append((subj, fac_name, "Lecture Room 2"))
                else:
                    if len(shifts["Shift 1"]) < periods_per_day:
                        shifts["Shift 1"].append((subj, fac_name, "Lecture Room 1"))
            else:
                if len(shifts["Shift 1"]) < periods_per_day:
                    shifts["Shift 1"].append((subj, fac_name, "Lecture Room 1"))

            day_index += 1

        # Fill remaining slots
        for day in range(working_days):
            for shift in ["Shift 1", "Shift 2"]:
                while len(timetable[branch_name][day][shift]) < periods_per_day:
                    timetable[branch_name][day][shift].append(("FREE", "-", "-"))

    # Convert faculty_workload ids -> names for API
    faculty_workload_named = {id_to_name[fid]: load for fid, load in faculty_workload.items()}

    return timetable, faculty_workload_named, subject_faculty_map, dept_workload

# -------------------------------
# Print Timetable (Debug)
# -------------------------------
def print_timetable(timetable, faculty_workload, subject_faculty_map, dept_workload):
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    for branch, schedule in timetable.items():
        print(f"\n=== Timetable for {branch} ===")
        for d, shifts in schedule.items():
            print(f"\n{days[d]}:")
            for shift, slots in shifts.items():
                print(f"  {shift}:")
                for period, cls in enumerate(slots, 1):
                    subject, faculty, room = cls
                    print(f"    Period {period}: {subject} ({room}) by {faculty}")
    print("\n=== Faculty Workload ===")
    for fac, load in faculty_workload.items():
        print(f"{fac}: {load} classes")

# -------------------------------
# Flask Routes
# -------------------------------
@app.route('/generate-timetable', methods=['POST'])
def generate_timetable_route():
    data = request.get_json()
    print("Received data:", data)

    save_to_database(data)
    max_load = data.get("maxLecturesPerFaculty", 10)

    timetable, faculty_workload, subject_faculty_map, dept_workload = generate_timetable(max_load)

    print_timetable(timetable, faculty_workload, subject_faculty_map, dept_workload)

    return jsonify({
        "timetable": timetable,
        "facultyWorkload": faculty_workload,
        "subjectFacultyMap": {k: list(v) for k, v in subject_faculty_map.items()},
        "departmentWorkload": dept_workload
    })

@app.route('/save-timetable', methods=['POST'])
def save_timetable():
    data = request.get_json()
    timetable = data.get("timetable")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE final_timetable")
    cursor.execute("INSERT INTO final_timetable (data) VALUES (%s)", (json.dumps(timetable),))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Timetable saved successfully"})

@app.route('/get-saved-timetable', methods=['GET'])
def get_saved_timetable():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT data FROM final_timetable LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return jsonify({"timetable": json.loads(row["data"])})
    return jsonify({"timetable": None})

# -------------------------------
# Run Flask App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
