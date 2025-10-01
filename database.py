import sqlite3
import bcrypt
from datetime import datetime

# ------------------- Database Setup -------------------
DB_FILE = "smart_study_buddy.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Users table for authentication
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, 
                  username TEXT UNIQUE, 
                  email TEXT UNIQUE,
                  password_hash TEXT,
                  created_date TEXT)''')
    
    # Study goals table with user_id
    c.execute('''CREATE TABLE IF NOT EXISTS study_goals
                 (id INTEGER PRIMARY KEY, 
                  user_id INTEGER, 
                  goal TEXT, 
                  created_date TEXT, 
                  completed BOOLEAN,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Study sessions table with user_id
    c.execute('''CREATE TABLE IF NOT EXISTS study_sessions
                 (id INTEGER PRIMARY KEY, 
                  user_id INTEGER,
                  score INTEGER, 
                  total_questions INTEGER, 
                  date TEXT, 
                  type TEXT,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Personal notes table
    c.execute('''CREATE TABLE IF NOT EXISTS personal_notes
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  topic TEXT,
                  content TEXT,
                  created_date TEXT,
                  last_modified TEXT,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()

init_db()

# ------------------- Authentication Functions -------------------
def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(username, email, password):
    """Create a new user in the database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        password_hash = hash_password(password)
        c.execute('INSERT INTO users (username, email, password_hash, created_date) VALUES (?, ?, ?, ?)',
                  (username, email, password_hash, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username or email already exists
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate a user"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    
    if user and verify_password(password, user[2]):
        return {'id': user[0], 'username': user[1]}
    return None

# ------------------- Database Utilities -------------------
def add_study_goal(goal, user_id):
    if not user_id:
        return False
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO study_goals (user_id, goal, created_date, completed) VALUES (?, ?, ?, ?)',
              (user_id, goal, datetime.now().strftime("%Y-%m-%d"), False))
    conn.commit()
    conn.close()
    return True

def mark_goal_complete(goal_id, user_id):
    if not user_id:
        return False
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE study_goals SET completed = ? WHERE id = ? AND user_id = ?', 
              (True, goal_id, user_id))
    conn.commit()
    conn.close()
    return True

def delete_goal(goal_id, user_id):
    if not user_id:
        return False
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM study_goals WHERE id = ? AND user_id = ?', (goal_id, user_id))
    conn.commit()
    conn.close()
    return True

def save_study_session(score, total_questions, session_type, user_id):
    if not user_id:
        return False
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO study_sessions (user_id, score, total_questions, date, type) VALUES (?, ?, ?, ?, ?)',
              (user_id, score, total_questions, datetime.now().strftime("%Y-%m-%d"), session_type))
    conn.commit()
    conn.close()
    return True

def load_study_goals(user_id):
    if not user_id:
        return []
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM study_goals WHERE user_id = ?", (user_id,))
    goals = [{'id': row[0], 'goal': row[2], 'created_date': row[3], 'completed': bool(row[4])} for row in c.fetchall()]
    conn.close()
    return goals

def load_study_sessions(user_id):
    if not user_id:
        return []
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM study_sessions WHERE user_id = ?", (user_id,))
    sessions = [{'id': row[0], 'score': row[2], 'total_questions': row[3], 'date': row[4], 'type': row[5]} for row in c.fetchall()]
    conn.close()
    return sessions

# ------------------- Personal Notes Functions -------------------
def save_personal_note(topic, content, user_id):
    """Save a personal note"""
    if not user_id:
        return False
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO personal_notes (user_id, topic, content, created_date, last_modified) VALUES (?, ?, ?, ?, ?)',
              (user_id, topic, content, current_time, current_time))
    conn.commit()
    conn.close()
    return True

def update_personal_note(note_id, topic, content, user_id):
    """Update an existing note"""
    if not user_id:
        return False
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('UPDATE personal_notes SET topic = ?, content = ?, last_modified = ? WHERE id = ? AND user_id = ?',
              (topic, content, current_time, note_id, user_id))
    conn.commit()
    conn.close()
    return True

def delete_personal_note(note_id, user_id):
    """Delete a personal note"""
    if not user_id:
        return False
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM personal_notes WHERE id = ? AND user_id = ?', (note_id, user_id))
    conn.commit()
    conn.close()
    return True

def load_personal_notes(user_id):
    """Load all personal notes for the current user"""
    if not user_id:
        return []
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM personal_notes WHERE user_id = ? ORDER BY last_modified DESC", (user_id,))
    notes = [{'id': row[0], 'topic': row[2], 'content': row[3], 'created_date': row[4], 'last_modified': row[5]} for row in c.fetchall()]
    conn.close()
    return notes