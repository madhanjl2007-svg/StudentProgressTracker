from flask import Flask, render_template, request, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "student_progress_secret"

# -------------------------------------------------
# Default values
# -------------------------------------------------

points = 20
completed = 1

assignment_status = "Submitted"
dbms_status = "Not Submitted"
python_status = "Not Submitted"


# -------------------------------------------------
# Database
# -------------------------------------------------

def create_database():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            username TEXT PRIMARY KEY,
            points INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            assignment_status TEXT DEFAULT 'Not Submitted',
            dbms_status TEXT DEFAULT 'Not Submitted',
            python_status TEXT DEFAULT 'Not Submitted'
        )
    """)

    # Add missing columns if old database is being used
    try:
        cursor.execute("""
            ALTER TABLE students
            ADD COLUMN assignment_status TEXT DEFAULT 'Not Submitted'
        """)
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("""
            ALTER TABLE students
            ADD COLUMN dbms_status TEXT DEFAULT 'Not Submitted'
        """)
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("""
            ALTER TABLE students
            ADD COLUMN python_status TEXT DEFAULT 'Not Submitted'
        """)
    except sqlite3.OperationalError:
        pass

    # Create Madhan account/data
    cursor.execute("""
        INSERT OR IGNORE INTO students
        (username, points, completed, assignment_status,
         dbms_status, python_status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "Madhan",
        20,
        1,
        "Submitted",
        "Not Submitted",
        "Not Submitted"
    ))

    conn.commit()
    conn.close()


# -------------------------------------------------
# Login page
# -------------------------------------------------

@app.route("/")
def home():
    return render_template("login.html")


# -------------------------------------------------
# Login
# -------------------------------------------------

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    session["username"] = username
    session["role"] = role

    if role == "student":

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT points, completed,
                   assignment_status,
                   dbms_status,
                   python_status
            FROM students
            WHERE username = ?
        """, (username,))

        student = cursor.fetchone()

        # If new student, create account
        if not student:

            cursor.execute("""
                INSERT INTO students
                (username, points, completed,
                 assignment_status,
                 dbms_status,
                 python_status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                username,
                0,
                0,
                "Not Submitted",
                "Not Submitted",
                "Not Submitted"
            ))

            conn.commit()

            points_value = 0
            completed_value = 0
            assignment_value = "Not Submitted"
            dbms_value = "Not Submitted"
            python_value = "Not Submitted"

        else:

            points_value = student[0]
            completed_value = student[1]
            assignment_value = student[2]
            dbms_value = student[3]
            python_value = student[4]

        conn.close()

        # Progress
        progress = round((completed_value / 3) * 100)

        if progress > 100:
            progress = 100

        # Badge
        if points_value >= 100:
            badge = "🥇 Gold"
        elif points_value >= 50:
            badge = "🥈 Silver"
        elif points_value >= 30:
            badge = "🥉 Bronze"
        else:
            badge = "🌱 Beginner"

        return render_template(
            "dashboard.html",
            username=username,
            points=points_value,
            progress=progress,
            badge=badge,
            assignment_status=assignment_value,
            dbms_status=dbms_value,
            python_status=python_value
        )

    else:

        return render_template(
            "faculty_dashboard.html",
            username=username
        )


# -------------------------------------------------
# Java Assignment Upload
# -------------------------------------------------

@app.route("/upload", methods=["POST"])
def upload():

    username = session.get("username", "Madhan")

    file = request.files.get("assignment")

    if file:

        os.makedirs("uploads", exist_ok=True)

        file.save(
            os.path.join(
                "uploads",
                file.filename
            )
        )

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE students
            SET assignment_status = ?
            WHERE username = ?
        """, (
            "Submitted",
            username
        ))

        conn.commit()
        conn.close()

        return "Java Assignment uploaded successfully! ✅"

    return "No file selected."


# -------------------------------------------------
# DBMS Assignment Upload
# -------------------------------------------------

@app.route("/upload_dbms", methods=["POST"])
def upload_dbms():

    username = session.get("username", "Madhan")

    file = request.files.get("dbms_assignment")

    if file:

        os.makedirs("uploads", exist_ok=True)

        file.save(
            os.path.join(
                "uploads",
                file.filename
            )
        )

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE students
            SET dbms_status = ?
            WHERE username = ?
        """, (
            "Submitted",
            username
        ))

        conn.commit()
        conn.close()

        return "DBMS Assignment uploaded successfully! ✅"

    return "No file selected."


# -------------------------------------------------
# Python Assignment Upload
# -------------------------------------------------

@app.route("/upload_python", methods=["POST"])
def upload_python():

    username = session.get("username", "Madhan")

    file = request.files.get("python_assignment")

    if file:

        os.makedirs("uploads", exist_ok=True)

        file.save(
            os.path.join(
                "uploads",
                file.filename
            )
        )

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE students
            SET python_status = ?
            WHERE username = ?
        """, (
            "Submitted",
            username
        ))

        conn.commit()
        conn.close()

        return "Python Assignment uploaded successfully! ✅"

    return "No file selected."


# -------------------------------------------------
# Approve Java Assignment
# -------------------------------------------------

@app.route("/approve", methods=["POST"])
def approve():

    username = session.get("username", "Madhan")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT points, completed, assignment_status
        FROM students
        WHERE username = ?
    """, (username,))

    student = cursor.fetchone()

    if student:

        current_points = student[0]
        current_completed = student[1]
        current_status = student[2]

        if current_status == "Submitted":

            new_points = current_points + 10
            new_completed = current_completed + 1

            if new_completed > 3:
                new_completed = 3

            cursor.execute("""
                UPDATE students
                SET points = ?,
                    completed = ?,
                    assignment_status = ?
                WHERE username = ?
            """, (
                new_points,
                new_completed,
                "Approved",
                username
            ))

            conn.commit()
            conn.close()

            return "Assignment Approved! ⭐ You earned 10 points!"

        else:

            conn.close()

            return "Assignment is already approved! ✅"

    conn.close()

    return "Student not found."


# -------------------------------------------------
# AI Assignment Verification Page
# -------------------------------------------------

@app.route("/ai_verify")
def ai_verify():

    return render_template("ai_verify.html")


# -------------------------------------------------
# AI Assignment Verification
# -------------------------------------------------

@app.route("/check_assignment", methods=["POST"])
def check_assignment():

    file_path = os.path.join(
        os.path.dirname(__file__),
        "uploads",
        "fake java assignment"
    )

    # Try .txt if the file has extension
    if not os.path.exists(file_path):

        file_path = os.path.join(
            os.path.dirname(__file__),
            "uploads",
            "fake java assignment.txt"
        )

    if not os.path.exists(file_path):

        return "Assignment file not found ❌"

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()

        if "java" in content.lower():

            result = "Relevant ✅"
            confidence = 92

        else:

            result = "Not clearly related ❌"
            confidence = 40

        return f"""
        <h1>🤖 AI Assignment Verification</h1>

        <h2>Result: {result}</h2>

        <p>Confidence: {confidence}%</p>

        <p>Assignment read successfully!</p>

        <hr>

        <a href="/ai_verify">Back to AI Verification</a>
        """

    except Exception as e:

        return f"Error reading assignment: {e}"


# -------------------------------------------------
# Run application
# -------------------------------------------------

if __name__ == "__main__":

    create_database()

    app.run(
        debug=True
    )