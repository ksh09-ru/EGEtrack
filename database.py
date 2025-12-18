import sqlite3

conn = sqlite3.connect("examstrack.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    schedule TEXT,
    subjects TEXT,
    weak_topics TEXT
)
""")

conn.commit()


def add_user(user_id):
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()


def update_field(user_id, field, value):
    cursor.execute(
        f"UPDATE users SET {field} = ? WHERE user_id = ?",
        (value, user_id)
    )
    conn.commit()


def get_user(user_id):
    cursor.execute(
        "SELECT schedule, subjects, weak_topics FROM users WHERE user_id = ?",
        (user_id,)
    )
    return cursor.fetchone()