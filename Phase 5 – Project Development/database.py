import json
import sqlite3
from contextlib import contextmanager
from config import settings

@contextmanager
def get_db():
    conn = sqlite3.connect(settings.database_url)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            input_data TEXT NOT NULL,
            result_data TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

def create_user(email, full_name, password_hash):
    with get_db() as db:
        cur = db.execute("INSERT INTO users(email,full_name,password_hash) VALUES(?,?,?)", (email.lower(), full_name, password_hash))
        return cur.lastrowid

def get_user_by_email(email):
    with get_db() as db:
        return db.execute("SELECT * FROM users WHERE email=?", (email.lower(),)).fetchone()

def get_user_by_id(user_id):
    with get_db() as db:
        return db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

def save_recommendation(user_id, category, input_data, result_data):
    with get_db() as db:
        cur = db.execute("INSERT INTO recommendations(user_id,category,input_data,result_data) VALUES(?,?,?,?)",
                         (user_id, category, json.dumps(input_data), json.dumps(result_data)))
        return cur.lastrowid

def list_history(user_id):
    with get_db() as db:
        return db.execute("SELECT * FROM recommendations WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()

def get_recommendation(user_id, rec_id):
    with get_db() as db:
        return db.execute("SELECT * FROM recommendations WHERE id=? AND user_id=?", (rec_id, user_id)).fetchone()
