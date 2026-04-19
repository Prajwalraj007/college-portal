from flask import Flask
import os
import mysql.connector

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# -------------------------
# DATABASE CONNECTION (SAFE + TIMEOUT)
# -------------------------
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE"),
            port=int(os.getenv("MYSQLPORT", 3306)),
            connection_timeout=5   # 🔥 prevents 502
        )
    except Exception as e:
        print("DB ERROR:", e)
        return None

# -------------------------
# BASIC ROUTES
# -------------------------
@app.route("/")
def home():
    return "SERVER LIVE ✅"

@app.route("/test")
def test():
    return "APP WORKING 🚀"

# -------------------------
# DB TEST ROUTE (IMPORTANT)
# -------------------------
@app.route("/test-db")
def test_db():
    conn = get_db_connection()
    if conn:
        conn.close()
        return "DB CONNECTED ✅"
    else:
        return "DB FAILED ❌"

# NOTE:
# ❌ No app.run() needed for Railway (Gunicorn handles it)