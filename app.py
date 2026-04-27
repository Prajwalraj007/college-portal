from flask import Flask, render_template, request, session, redirect, url_for, flash
import os
import mysql.connector
from werkzeug.utils import secure_filename
import urllib.parse

app = Flask(__name__)

print("FLASK APP STARTING...")

# -------------------------
# SECRET KEY
# -------------------------
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# -------------------------
# UPLOAD FOLDER
# -------------------------
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# DATABASE CONNECTION
# -------------------------
def get_db_connection():
    url = os.getenv("MYSQL_URL")

    if not url:
        print("MYSQL_URL NOT FOUND")
        return None

    try:
        parsed = urllib.parse.urlparse(url)

        return mysql.connector.connect(
            host=parsed.hostname,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/'),
            port=parsed.port,
            connection_timeout=5
        )

    except Exception as e:
        print("DB ERROR:", e)
        return None


# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# COURSE ROUTES
# -------------------------
@app.route("/course/<name>")
def course(name):
    return render_template("course.html", course=name)


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
# PAPERS
# -------------------------
@app.route("/papers/<course>/<int:sem>")
def papers(course, sem):

    conn = get_db_connection()
    if not conn:
        return "Database not connected"

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM question_papers
        WHERE course=%s AND semester=%s
    """, (course, sem))

    papers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("papers.html", papers=papers, course=course, sem=sem)


# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        if not conn:
            return "Database not connected"

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
            return "Invalid Login"

    return render_template("login.html")


# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.pop("teacher", None)
    return redirect(url_for("home"))


# -------------------------
# UPLOAD
# -------------------------
@app.route("/upload")
def upload():
    if not session.get("teacher"):
        return redirect(url_for("login"))

    return render_template("upload.html")


@app.route("/upload-paper", methods=["POST"])
def upload_paper():

    if not session.get("teacher"):
        return "Unauthorized"

    course = request.form["course"]
    semester = request.form["semester"]
    subject = request.form["subject"]
    file = request.files["file"]

    if file and file.filename != "":

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        db_path = f"uploads/{filename}"

        conn = get_db_connection()
        if not conn:
            return "Database not connected"

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO question_papers
            (course, semester, subject, filename, file_path)
            VALUES (%s, %s, %s, %s, %s)
        """, (course, semester, subject, filename, db_path))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Uploaded successfully!", "success")
        return redirect(url_for("papers", course=course, sem=semester))

    return "Upload Failed"


# -------------------------
# DELETE
# -------------------------
@app.route("/delete/<int:id>/<course>/<int:sem>")
def delete_paper(id, course, sem):

    if not session.get("teacher"):
        return "Unauthorized"

    conn = get_db_connection()
    if not conn:
        return "Database not connected"

    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT file_path FROM question_papers WHERE id=%s", (id,))
    paper = cursor.fetchone()

    if paper:
        full_path = os.path.join("static", paper["file_path"])

        if os.path.exists(full_path):
            os.remove(full_path)

        cursor.execute("DELETE FROM question_papers WHERE id=%s", (id,))
        conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("papers", course=course, sem=sem))


# -------------------------
# DEBUG ROUTES (IMPORTANT)
# -------------------------
@app.route("/test")
def test():
    return "FLASK IS RUNNING"


@app.route("/ping")
def ping():
    return "pong"


@app.route("/health")
def health():
    return "OK"


@app.route("/debug")
def debug():
    return {
        "status": "running",
        "port": os.getenv("PORT"),
        "mysql": "set" if os.getenv("MYSQL_URL") else "missing"
    }


# -------------------------
# RAILWAY ENTRY
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)