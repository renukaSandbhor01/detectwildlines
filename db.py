"""
db.py — All MySQL access for WildLens.

Uses mysql.connector exactly the way you already learned:
connect() -> cursor() -> execute() -> commit()/fetch...()

Update DB_CONFIG below with your own MySQL username/password.
"""

import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",   # <-- change this
    "database": "wildlens"
}


def get_connection():
    """Open a fresh connection. Each request gets its own connection
    and closes it when done — simplest and safest pattern for a small app."""
    return mysql.connector.connect(**DB_CONFIG)


# ---------------- USERS ----------------

def create_user(username, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
        return True
    except Error:
        return False  # likely a duplicate username
    finally:
        cursor.close()
        conn.close()


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


# ---------------- PREDICTIONS ----------------

def save_prediction(user_id, image_filename, predicted_label, confidence):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO predictions (user_id, image_filename, predicted_label, confidence) "
        "VALUES (%s, %s, %s, %s)",
        (user_id, image_filename, predicted_label, confidence)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_history_for_user(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM predictions WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
