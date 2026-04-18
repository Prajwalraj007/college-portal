from flask import Flask, render_template, request, session, redirect, url_for 
import os
import mysql.connector
from werkzeug.utils import secure_filename
from flask import flash

app = Flask(__name__)
app.secret_key = "secret123"

# -------------------------
# CONFIG
# -------------------------
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# DATABASE CONNECTION
# -------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Raj@2512",
        database="college_portal"
    )

# -------------------------
# HOME PAGE
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------
# COURSE PAGES
# -------------------------
@app.route("/course/<name>")
def course(name):
    return render_template("course.html", course=name)

# Optional direct routes
@app.route("/bca")
def bca():
    return redirect(url_for("course", name="bca"))

@app.route("/bsc")
def bsc():
    return redirect(url_for("course", name="bsc"))

@app.route("/bcom")
def bcom():
    return redirect(url_for("course", name="bcom"))

@app.route("/ba")
def ba():
    return redirect(url_for("course", name="ba"))

@app.route("/bba")
def bba():
    return redirect(url_for("course", name="bba"))

# -------------------------
# SEMESTER PAPERS
# -------------------------
@app.route("/papers/<course>/<int:sem>")
def papers(course, sem):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM question_papers
        WHERE course=%s AND semester=%s
    """, (course, sem))

    papers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("papers.html", papers=papers, sem=sem, course=course)

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM teachers WHERE email=%s AND password=%s",
            (email, password)
        )

        teacher = cursor.fetchone()

        cursor.close()
        conn.close()

        if teacher:
            session["teacher"] = teacher["id"]
            return redirect(url_for("home"))
        else:
            return "Invalid Login "

    return render_template("login.html")

# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.pop("teacher", None)
    return redirect(url_for("home"))

# -------------------------
# UPLOAD PAGE
# -------------------------
@app.route("/upload")
def upload():
    if not session.get("teacher"):
        return redirect(url_for("login"))

    return render_template("upload.html")

# -------------------------
# UPLOAD PAPER
# -------------------------
@app.route("/upload-paper", methods=["POST"])
def upload_paper():

    if not session.get("teacher"):
        return "Unauthorized "

    course = request.form["course"]
    semester = int(request.form["semester"])
    subject = request.form["subject"]
    file = request.files["file"]

    if file and file.filename != "":

        filename = secure_filename(file.filename)

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        db_path = f"uploads/{filename}"

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO question_papers
            (course, semester, subject, filename, file_path)
            VALUES (%s, %s, %s, %s, %s)
        """, (course, semester, subject, filename, db_path))

        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Paper uploaded successfully!", "success")
        return redirect(url_for("papers", course=course, sem=semester))
    return "Upload Failed ❌"

# -------------------------
# DELETE PAPER
# -------------------------
@app.route("/delete/<int:id>/<course>/<int:sem>")
def delete_paper(id, course, sem):

    if not session.get("teacher"):
        return "Unauthorized ❌"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT file_path FROM question_papers WHERE id=%s",
        (id,)
    )

    paper = cursor.fetchone()

    if paper:

        full_path = os.path.join("static", paper["file_path"])

        if os.path.exists(full_path):
            os.remove(full_path)

        cursor.execute(
            "DELETE FROM question_papers WHERE id=%s",
            (id,)
        )
        conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("papers", course=course, sem=sem))

# -------------------------
# RUN SERVER
# -------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)