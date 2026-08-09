
import os
import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD","YOUR_MYSQL_PASSWORD"),
    "database": os.environ.get("DB_NAME", "wildlens"),
}

# Aiven (and most cloud MySQL providers) require an SSL connection.
# Locally this stays unset and mysql-connector just connects normally.
_ssl_ca_path = os.environ.get("DB_SSL_CA_PATH")
if _ssl_ca_path:
    DB_CONFIG["ssl_ca"] = _ssl_ca_path
    DB_CONFIG["ssl_verify_cert"] = True


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
