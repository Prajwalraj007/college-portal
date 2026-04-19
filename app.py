from flask import Flask, render_template, request, session, redirect, url_for, flash
import os
import mysql.connector
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# -------------------------
# CONFIG
# -------------------------
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# DATABASE CONNECTION (SAFE)
# -------------------------
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("MYSQLHOST", "localhost"),
            user=os.getenv("MYSQLUSER", "root"),
            password=os.getenv("MYSQLPASSWORD", ""),
            database=os.getenv("MYSQLDATABASE", "railway"),
            port=int(os.getenv("MYSQLPORT", 3306))   # ✅ FIX HERE
        )
    except Exception as e:
        print("DB CONNECTION ERROR:", e)
        return None

# -------------------------
# TEST ROUTE
# -------------------------
@app.route("/test")
def test():
    return "App is running!"

# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    return "HOME WORKING ✅"

# -------------------------
# RUN SERVER
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)