import sqlite3
import json
from datetime import datetime

DATABASE = 'attendance.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            face_encoding TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Attendance table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def check_name_exists(name):
    """Check if a name already exists in the database"""
    conn = get_db_connection()
    user = conn.execute('SELECT name FROM users WHERE LOWER(name) = LOWER(?)', (name,)).fetchone()
    conn.close()
    return user is not None

def add_user(name, face_encoding):
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (name, face_encoding) VALUES (?, ?)',
            (name, json.dumps(face_encoding))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    
    result = []
    for user in users:
        result.append({
            'id': user['id'],
            'name': user['name'],
            'face_encoding': json.loads(user['face_encoding']),
            'created_at': user['created_at']
        })
    return result

def add_attendance(name, timestamp):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO attendance (name, timestamp) VALUES (?, ?)',
        (name, timestamp)
    )
    conn.commit()
    conn.close()

def get_all_attendance():
    conn = get_db_connection()
    records = conn.execute(
        'SELECT * FROM attendance ORDER BY timestamp DESC'
    ).fetchall()
    conn.close()
    
    result = []
    for record in records:
        result.append({
            'id': record['id'],
            'name': record['name'],
            'timestamp': record['timestamp']
        })
    return result