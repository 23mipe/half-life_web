import os
import json
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
return psycopg2.connect(DATABASE_URL)

def init_db():
conn = get_connection()
cur = conn.cursor()

```
cur.execute("""
CREATE TABLE IF NOT EXISTS guest_session (
    session_id TEXT PRIMARY KEY,
    history TEXT,
    notes TEXT,
    user_id INTEGER,
    last_visit TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS user_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    section_name TEXT,
    visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS user_notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    note_text TEXT,
    section TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

conn.commit()
cur.close()
conn.close()
```

def save_session(session_id, history, notes):
conn = get_connection()
cur = conn.cursor()

```
cur.execute("""
    INSERT INTO guest_session
    (session_id, history, notes, last_visit)
    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
    ON CONFLICT (session_id)
    DO UPDATE SET
        history = EXCLUDED.history,
        notes = EXCLUDED.notes,
        last_visit = CURRENT_TIMESTAMP
""", (session_id, history, notes))

conn.commit()
cur.close()
conn.close()
```

def load_session(session_id):
conn = get_connection()
cur = conn.cursor()

```
cur.execute("""
    SELECT history, notes
    FROM guest_session
    WHERE session_id = %s
""", (session_id,))

row = cur.fetchone()

cur.close()
conn.close()

return row if row else ("[]", "[]")
```

def create_user(username, email, password):
pw_hash = bcrypt.hashpw(
password.encode("utf-8"),
bcrypt.gensalt()
)

```
conn = get_connection()
cur = conn.cursor()

try:
    cur.execute("""
        INSERT INTO users
        (username, email, password_hash)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (username, email, psycopg2.Binary(pw_hash)))

    user_id = cur.fetchone()[0]

    conn.commit()
    return user_id

except psycopg2.Error:
    conn.rollback()
    return None

finally:
    cur.close()
    conn.close()
```

def get_user_by_username(username):
conn = get_connection()
cur = conn.cursor()

```
cur.execute("""
    SELECT id, username, email, password_hash
    FROM users
    WHERE username = %s
""", (username,))

user = cur.fetchone()

cur.close()
conn.close()

return user
```

def migrate_guest_data_to_user(user_id, guest_id):
hist_json, notes_json = load_session(guest_id)

```
history = json.loads(hist_json)
notes = json.loads(notes_json)

conn = get_connection()
cur = conn.cursor()

for sec in history:
    cur.execute("""
        INSERT INTO user_history
        (user_id, section_name, visited_at)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
    """, (user_id, sec))

for note in notes:
    cur.execute("""
        INSERT INTO user_notes
        (user_id, note_text, section, created_at)
        VALUES (%s, %s, %s, %s)
    """, (
        user_id,
        note["text"],
        note.get("section", "general"),
        note.get(
            "timestamp",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    ))

conn.commit()

cur.close()
conn.close()
```

def add_user_history(user_id, section_name):
conn = get_connection()
cur = conn.cursor()

```
cur.execute("""
    INSERT INTO user_history
    (user_id, section_name)
    VALUES (%s, %s)
""", (user_id, section_name))

conn.commit()

cur.close()
conn.close()
```

def get_user_history(user_id):
conn = get_connection()
cur = conn.cursor()

```
cur.execute("""
    SELECT section_name, visited_at
    FROM user_history
    WHERE user_id = %s
    ORDER BY visited_at DESC
""", (user_id,))

rows = cur.fetchall()

cur.close()
conn.close()

return rows
```

def add_user_note(user_id, note_text, section='general'):
conn = get_connection()
cur = conn.cursor()

```
cur.execute("""
    INSERT INTO user_notes
    (user_id, note_text, section)
    VALUES (%s, %s, %s)
""", (user_id, note_text, section))

conn.commit()

cur.close()
conn.close()
```

def get_user_notes(user_id):
conn = get_connection()
cur = conn.cursor()

```
cur.execute("""
    SELECT note_text, section, created_at
    FROM user_notes
    WHERE user_id = %s
    ORDER BY created_at DESC
""", (user_id,))

rows = cur.fetchall()

cur.close()
conn.close()

return rows
```
