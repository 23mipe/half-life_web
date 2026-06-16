import sqlite3
import os
import json
import bcrypt
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "half-life.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS guest_session (
        session_id TEXT PRIMARY KEY,
        history TEXT,
        notes TEXT,
        last_visit TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        section_name TEXT,
        visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        note_text TEXT,
        section TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )''')

    try:
        cursor.execute('ALTER TABLE guest_session ADD COLUMN user_id INTEGER')
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

def save_session(session_id, history, notes):
    conn = get_connection()
    conn.execute('INSERT OR REPLACE INTO guest_session (session_id, history, notes, last_visit) VALUES (?,?,?, CURRENT_TIMESTAMP)',
                 (session_id, history, notes))
    conn.commit()
    conn.close()

def load_session(session_id):
    conn = get_connection()
    row = conn.execute('SELECT history, notes FROM guest_session WHERE session_id=?', (session_id,)).fetchone()
    conn.close()
    return row if row else ("[]", "[]")

def create_user(username, email, password):
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = get_connection()
    try:
        cur = conn.execute('INSERT INTO users (username, email, password_hash, created_at) VALUES (?,?,?, ?)',
                           (username, email, pw_hash, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_connection()
    user = conn.execute('SELECT id, username, email, password_hash FROM users WHERE username=?', (username,)).fetchone()
    conn.close()
    return user

def migrate_guest_data_to_user(user_id, guest_id):
    hist_json, notes_json = load_session(guest_id)
    history = json.loads(hist_json)
    notes = json.loads(notes_json)
    conn = get_connection()
    for sec in history:
        conn.execute('INSERT INTO user_history (user_id, section_name, visited_at) VALUES (?,?, CURRENT_TIMESTAMP)',
                     (user_id, sec))
    for note in notes:
        conn.execute('INSERT INTO user_notes (user_id, note_text, section, created_at) VALUES (?,?,?,?)',
                     (user_id, note['text'], note.get('section', 'general'),
                      note.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))))
    conn.commit()
    conn.close()

def add_user_history(user_id, section_name):
    conn = get_connection()
    conn.execute('INSERT INTO user_history (user_id, section_name) VALUES (?,?)', (user_id, section_name))
    conn.commit()
    conn.close()

def get_user_history(user_id):
    conn = get_connection()
    rows = conn.execute('SELECT section_name, visited_at FROM user_history WHERE user_id=? ORDER BY visited_at DESC',
                        (user_id,)).fetchall()
    conn.close()
    return rows

def add_user_note(user_id, note_text, section='general'):
    conn = get_connection()
    conn.execute('INSERT INTO user_notes (user_id, note_text, section) VALUES (?,?,?)',
                 (user_id, note_text, section))
    conn.commit()
    conn.close()

def get_user_notes(user_id):
    conn = get_connection()
    rows = conn.execute(
        'SELECT note_text, section, created_at FROM user_notes WHERE user_id=? ORDER BY created_at DESC',
        (user_id,)).fetchall()
    conn.close()
    return rows
