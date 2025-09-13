import mysql.connector
import random
import json
from collections import defaultdict
from flask import Flask, request, jsonify
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)

# -----------------------------
# Genetic Algorithm Parameters
# -----------------------------
POPULATION_SIZE = 100
MAX_GENERATIONS = 500
MUTATION_RATE = 0.1
WORKING_DAYS = 5
MORNING_SHIFT_PERIODS = 4
EVENING_SHIFT_PERIODS = 2

# -----------------------------
# Database Connection
# -----------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sharma346",
        database="timetable_db"
    )

# -----------------------------
# Save Initial Payload
# -----------------------------
def save_to_database(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("TRUNCATE TABLE branches")
    cursor.execute("TRUNCATE TABLE subjects")
    cursor.execute("TRUNCATE TABLE practicals")
    cursor.execute("TRUNCATE TABLE faculties")
    cursor.execute("TRUNCATE TABLE faculty_subjects")
    cursor.execute("TRUNCATE TABLE departments")
    cursor.execute("TRUNCATE TABLE lecture_rooms")
    cursor.execute("TRUNCATE TABLE labs")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    # Branches + subjects + practicals
    for branch in data.get("branches", []):
        cursor.execute(
            "INSERT INTO branches (name, total_students, class_hours_per_day, period_duration) VALUES (%s, %s, %s, %s)",
            (branch["name"], branch["totalStudents"], branch["classHoursPerDay"], branch["periodDuration"])
        )
        branch_id = cursor.lastrowid

        for subj in branch.get("subjects", []):
            cursor.execute("INSERT INTO subjects (branch_id, subject_name) VALUES (%s,%s)", (branch_id, subj))

        for prac in branch.get("practicals", []):
            cursor.execute("INSERT INTO practicals (branch_id, name, classes_per_week) VALUES (%s,%s,%s)",
                           (branch_id, prac["name"], prac["classesPerWeek"]))

    # Lecture room
    lecture_rooms_data = data.get("lectureRooms")
    if lecture_rooms_data:
        cursor.execute("INSERT INTO lecture_rooms (total_rooms, max_capacity) VALUES (%s,%s)",
                       (lecture_rooms_data["totalRooms"], lecture_rooms_data["maxCapacity"]))

    # Labs
    for lab in data.get("labs", []):
        cursor.execute("INSERT INTO labs (type, num_labs, max_capacity) VALUES (%s,%s,%s)",
                       (lab["type"], lab["numLabs"], lab["maxCapacity"]))

    # Departments + faculties
    for dept in data.get("departments", []):
        cursor.execute("INSERT INTO departments (name) VALUES (%s)", (dept["name"],))
        dept_id = cursor.lastrowid
        for fac in dept.get("faculties", []):
            cursor.execute("INSERT INTO faculties (department_id, name) VALUES (%s,%s)", (dept_id, fac["name"]))
            fac_id = cursor.lastrowid
            for subj in fac.get("assignedSubjects", []):
                cursor.execute("INSERT INTO faculty_subjects (faculty_id, subject_name) VALUES (%s,%s)",
                               (fac_id, subj))

    conn.commit()
    cursor.close()
    conn.close()

# -----------------------------
# Fetch Data
# -----------------------------
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
    cursor.execute("SELECT * FROM lecture_rooms LIMIT 1")
    lecture_rooms = cursor.fetchone()
    cursor.execute("SELECT * FROM labs")
    labs = cursor.fetchall()
    cursor.close()
    conn.close()
    return branches, subjects, practicals, faculties, faculty_subjects, lecture_rooms, labs

# -----------------------------
# Timetable Generator (Genetic Algorithm)
# -----------------------------
def generate_timetable_ga(max_lectures_per_faculty=10):
    branches, subjects, practicals, faculties, faculty_subjects, lecture_rooms, labs = fetch_data()

    faculty_data = {f["id"]: {"name": f["name"], "subjects": []} for f in faculties}
    for fs in faculty_subjects:
        if fs["faculty_id"] in faculty_data:
            faculty_data[fs["faculty_id"]]["subjects"].append(fs["subject_name"].strip().lower())

    branch_data = {}
    for b in branches:
        branch_id = b["id"]
        branch_subjects = [s["subject_name"].strip().lower() for s in subjects if s["branch_id"] == branch_id]
        branch_practicals = [p["name"].strip().lower() for p in practicals if p["branch_id"] == branch_id]

        needs_evening_shift = False
        if lecture_rooms:
            if b["total_students"] > (lecture_rooms["total_rooms"] * lecture_rooms["max_capacity"]):
                needs_evening_shift = True

        branch_data[branch_id] = {
            "name": b["name"],
            "total_students": b["total_students"],
            "periods_per_day": max(1, int(b.get("class_hours_per_day", 0)) // int(b.get("period_duration", 1))),
            "subjects": branch_subjects,
            "practicals": branch_practicals,
            "needs_evening_shift": needs_evening_shift
        }

    room_list = []
    if lecture_rooms and lecture_rooms.get("total_rooms"):
        for i in range(1, int(lecture_rooms["total_rooms"]) + 1):
            room_list.append({"id": f"LectureRoom-{i}", "capacity": lecture_rooms["max_capacity"], "type": "Lecture"})
    for lab in labs:
        for i in range(1, int(lab["num_labs"]) + 1):
            room_list.append({"id": f"{lab['type']}-Lab-{i}", "capacity": lab["max_capacity"], "type": "Lab"})
    if not room_list:
        room_list.append({"id": "Room-1", "capacity": 9999, "type": "Generic"})

    # --- Genetic Algorithm Core ---

    def create_individual():
        """Creates a single random timetable (an 'individual')."""
        individual = {}
        for b_id, b_info in branch_data.items():
            branch_name = b_info["name"]
            total_students = b_info["total_students"]
            periods_per_day = b_info["periods_per_day"]

            morning_shift_rooms = [r for r in room_list if r["type"] == "Lecture"]
            if not morning_shift_rooms:
                morning_shift_rooms = [{"capacity": 9999}]

            morning_capacity_sum = sum(r["capacity"] for r in morning_shift_rooms)
            num_sections = max(1, math.ceil(total_students / morning_shift_rooms[0]["capacity"])) if morning_shift_rooms else 1
            section_size = math.ceil(total_students / num_sections)

            individual[branch_name] = {}
            for sec_idx in range(num_sections):
                sec_name = f"Section {sec_idx + 1}"
                shift_name = "Morning"
                if b_info["needs_evening_shift"] and sec_idx >= (num_sections // 2):
                    shift_name = "Evening"

                schedule = {f"Day {d+1}": [] for d in range(WORKING_DAYS)}

                for day_idx in range(WORKING_DAYS):
                    for period_idx in range(periods_per_day):
                        if random.random() < 0.2:
                            activity = "Free Period"
                            activity_type = "Free Period"
                            eligible_rooms = room_list
                            faculty_id = None
                        else:
                            is_practical_slot = b_info["practicals"] and random.choice([True, False])
                            
                            if is_practical_slot:
                                activity = random.choice(b_info["practicals"])
                                activity_type = "Practical"
                                eligible_rooms = [r for r in room_list if r["type"] == "Lab" and r["capacity"] >= section_size]
                            else:
                                activity = random.choice(b_info["subjects"]) if b_info["subjects"] else "Free Period"
                                activity_type = "Lecture"
                                eligible_rooms = [r for r in room_list if r["type"] == "Lecture" and r["capacity"] >= section_size]

                            eligible_faculties = [
                                f_id for f_id, f_info in faculty_data.items()
                                if activity.lower() in f_info["subjects"]
                            ]
                            faculty_id = random.choice(eligible_faculties) if eligible_faculties else None
                        
                        room = random.choice(eligible_rooms) if eligible_rooms else None
                        
                        schedule[f"Day {day_idx+1}"].append({
                            "period": period_idx + 1,
                            "subject": activity.title(),
                            "type": activity_type,
                            "faculty_id": faculty_id,
                            "room_id": room["id"] if room else "No suitable room"
                        })

                individual[branch_name][sec_name] = {
                    "shift": shift_name,
                    "schedule": schedule,
                    "section_size": section_size
                }
        return individual

    def fitness(individual):
        """Evaluates how good a timetable is based on conflicts."""
        score = 0
        faculty_workload = defaultdict(int)

        faculty_availability = defaultdict(lambda: defaultdict(set))
        room_availability = defaultdict(lambda: defaultdict(set))
        room_map = {r["id"]: r for r in room_list}

        for branch_name, sections in individual.items():
            for sec_name, sec_data in sections.items():
                schedule = sec_data["schedule"]
                section_size = sec_data["section_size"]
                for day_label, periods in schedule.items():
                    day_idx = int(day_label.split(" ")[1]) - 1
                    for slot in periods:
                        fac_id = slot["faculty_id"]
                        room_id = slot["room_id"]
                        period_idx = slot["period"] - 1

                        room_capacity = room_map.get(room_id, {}).get("capacity", 0)
                        if room_capacity < section_size:
                            score -= 2000

                        if fac_id and (day_idx, period_idx) in faculty_availability[fac_id]:
                            score -= 1000
                        else:
                            faculty_availability[fac_id][(day_idx, period_idx)] = sec_name

                        if (day_idx, period_idx) in room_availability[room_id]:
                            score -= 1000
                        else:
                            room_availability[room_id][(day_idx, period_idx)] = sec_name

                        if fac_id and slot["subject"].lower() not in faculty_data[fac_id]["subjects"] and slot["subject"].lower() != "free period":
                            score -= 500

                        room_type = room_map.get(room_id, {}).get("type", "Unknown")
                        if slot["type"] == "Lecture" and room_type != "Lecture":
                            score -= 500
                        if slot["type"] == "Practical" and room_type != "Lab":
                             score -= 500
                        if slot["type"] == "Free Period" and room_type not in ["Lecture", "Lab"]:
                             score -= 500

                        if fac_id and slot["subject"].lower() != "free period":
                            faculty_workload[fac_id] += 1
                            if faculty_workload[fac_id] > max_lectures_per_faculty:
                                score -= 1

        if score == 0:
            score += 10000

        return score

    def crossover(parent1, parent2):
        child = {}
        for branch_name in parent1:
            child[branch_name] = {}
            for sec_name in parent1[branch_name]:
                if random.random() > 0.5:
                    child[branch_name][sec_name] = parent1[branch_name][sec_name]
                else:
                    child[branch_name][sec_name] = parent2[branch_name][sec_name]
        return child

    def mutate(individual):
        for branch_name in individual:
            for sec_name, sec_data in individual[branch_name].items():
                if random.random() < MUTATION_RATE:
                    day = random.choice(list(sec_data["schedule"].keys()))
                    period_idx = random.randint(0, len(sec_data["schedule"][day]) - 1)
                    section_size = sec_data["section_size"]

                    b_id = next(b["id"] for b in branches if b["name"] == branch_name)
                    b_info = branch_data[b_id]

                    if random.random() < 0.2:
                        new_activity = "Free Period"
                        activity_type = "Free Period"
                        new_room = random.choice(room_list)
                        new_faculty_id = None
                    elif b_info["practicals"] and random.random() < 0.5:
                        new_activity = random.choice(b_info["practicals"])
                        eligible_rooms = [r for r in room_list if r["type"] == "Lab" and r["capacity"] >= section_size]
                        activity_type = "Practical"
                        new_room = random.choice(eligible_rooms) if eligible_rooms else None
                        eligible_faculties = [f_id for f_id, f_info in faculty_data.items() if new_activity.lower() in f_info["subjects"]]
                        new_faculty_id = random.choice(eligible_faculties) if eligible_faculties else None
                    elif b_info["subjects"]:
                        new_activity = random.choice(b_info["subjects"])
                        eligible_rooms = [r for r in room_list if r["type"] == "Lecture" and r["capacity"] >= section_size]
                        activity_type = "Lecture"
                        new_room = random.choice(eligible_rooms) if eligible_rooms else None
                        eligible_faculties = [f_id for f_id, f_info in faculty_data.items() if new_activity.lower() in f_info["subjects"]]
                        new_faculty_id = random.choice(eligible_faculties) if eligible_faculties else None
                    else:
                        continue

                    if new_room is None:
                        continue

                    individual[branch_name][sec_name]["schedule"][day][period_idx] = {
                        "period": period_idx + 1,
                        "subject": new_activity.title(),
                        "type": activity_type,
                        "faculty_id": new_faculty_id,
                        "room_id": new_room["id"]
                    }
        return individual

    population = [create_individual() for _ in range(POPULATION_SIZE)]

    for generation in range(MAX_GENERATIONS):
        fitness_scores = [(fitness(ind), ind) for ind in population]
        fitness_scores.sort(key=lambda x: x[0], reverse=True)

        best_individual = fitness_scores[0][1]
        best_fitness = fitness_scores[0][0]

        if best_fitness >= 10000:
            return process_final_timetable(best_individual, faculty_data, room_list)

        elite_count = POPULATION_SIZE // 2
        elite = [ind for score, ind in fitness_scores[:elite_count]]

        new_population = elite
        while len(new_population) < POPULATION_SIZE:
            parent1 = random.choice(elite)
            parent2 = random.choice(elite)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)

        population = new_population

    best_individual = fitness_scores[0][1]
    return process_final_timetable(best_individual, faculty_data, room_list)

def process_final_timetable(timetable_raw, faculty_data, room_list):
    final_timetable = {}
    warnings = []
    faculty_workload = defaultdict(int)
    room_map = {r["id"]: r for r in room_list}

    for branch_name, sections in timetable_raw.items():
        final_timetable[branch_name] = {}
        for sec_name, sec_data in sections.items():
            final_timetable[branch_name][sec_name] = {
                "shift": sec_data["shift"],
                "schedule": {}
            }
            for day_label, periods in sec_data["schedule"].items():
                final_timetable[branch_name][sec_name]["schedule"][day_label] = []
                for slot in periods:
                    fac_id = slot.get("faculty_id")
                    room_id = slot.get("room_id")

                    faculty_name = faculty_data.get(fac_id, {}).get("name", "Unassigned")

                    if not fac_id or not faculty_name:
                        warnings.append(f"No faculty assigned for {slot['subject']} in {branch_name} {sec_name} on {day_label} Period {slot['period']}")
                    else:
                        if slot["subject"].lower() != "free period":
                            faculty_workload[fac_id] += 1

                    room_name = room_map.get(room_id, {}).get("id", "Unassigned")

                    final_timetable[branch_name][sec_name]["schedule"][day_label].append({
                        "period": slot["period"],
                        "subject": slot["subject"],
                        "type": slot["type"],
                        "faculty": faculty_name,
                        "room": room_name
                    })

    faculty_workload_report = [
        {"id": fac_id, "name": faculty_data.get(fac_id, {}).get("name", "Unknown"), "workload": workload}
        for fac_id, workload in faculty_workload.items()
    ]

    return final_timetable, faculty_workload_report, warnings

# -----------------------------
# Routes
# -----------------------------
@app.route("/generate-timetable", methods=["POST"])
def generate_timetable_route():
    data = request.get_json()
    save_to_database(data)
    max_load = data.get("maxLecturesPerFaculty", 10)

    random.seed()
    timetable, workloads, warnings = generate_timetable_ga(max_load)

    return jsonify({"timetable": timetable, "facultyWorkload": workloads, "warnings": warnings})

@app.route("/save-timetable", methods=["POST"])
def save_timetable():
    data = request.get_json()
    timetable = data.get("timetable")
    conn = get_db_connection()
    cursor = conn.cursor()
    # TRUNCATE TABLE deletes all rows, effectively "clearing" the table
    cursor.execute("TRUNCATE TABLE final_timetable")
    cursor.execute("INSERT INTO final_timetable (data) VALUES (%s)", (json.dumps(timetable),))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Timetable saved successfully"})

@app.route("/get-saved-timetable", methods=["GET"])
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

# (Keep all existing imports and functions)

# -----------------------------
# New Routes for Dynamic Login
# -----------------------------
@app.route("/get-login-data", methods=["GET"])
def get_login_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch faculties with their IDs
    cursor.execute("SELECT id, name FROM faculties")
    faculties = cursor.fetchall()

    # Fetch branches
    cursor.execute("SELECT name FROM branches")
    branches = cursor.fetchall()

    cursor.close()
    conn.close()

    # The password is a static value for simplicity in this system
    # In a real-world app, this should be handled securely
    faculty_list = [{"id": f["id"], "name": f["name"], "password": "1234"} for f in faculties]
    branch_list = [b["name"] for b in branches]

    # For students, we'll just get the list of branches and use a generic password
    student_list = [{"name": f"student{i+1}", "password": "1234"} for i in range(5)] # Example, can be fetched from DB

    return jsonify({
        "faculties": faculty_list,
        "branches": branch_list,
        "students": student_list
    })

# (Keep all other existing routes and the main function)
if __name__ == "__main__":
    app.run(debug=True, port=5000)