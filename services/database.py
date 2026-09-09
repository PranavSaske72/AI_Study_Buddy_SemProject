import sqlite3
import hashlib
from pathlib import Path


# Database location
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DB_PATH = DATABASE_DIR / "study_buddy.db"


def get_connection():
    """Create a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def create_tables():
    """Create the users table if it doesn't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    """Convert a password into a secure hash."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(name, email, password):
    """Create a new user account."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        hashed_password = hash_password(password)

        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
            """,
            (name, email, hashed_password)
        )

        conn.commit()
        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."

    finally:
        conn.close()


def authenticate_user(email, password):
    """Check whether login credentials are correct."""
    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    cursor.execute(
        """
        SELECT id, name, email
        FROM users
        WHERE email = ? AND password = ?
        """,
        (email, hashed_password)
    )

    user = cursor.fetchone()
    conn.close()

    return user

def save_study_material(user_id, file_name, file_path):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO study_materials (user_id, file_name, file_path)
        VALUES (?, ?, ?)
        """,
        (user_id, file_name, file_path)
    )

    conn.commit()
    conn.close()


def get_study_materials(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, file_name, file_path, uploaded_at
        FROM study_materials
        WHERE user_id = ?
        ORDER BY uploaded_at DESC
        """,
        (user_id,)
    )

    materials = cursor.fetchall()
    conn.close()

    return materials

def save_study_material(user_id, file_name, file_path):
    """Save study material information."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO study_materials (user_id, file_name, file_path)
        VALUES (?, ?, ?)
        """,
        (user_id, file_name, file_path)
    )

    conn.commit()
    conn.close()


def get_study_materials(user_id):
    """Get all study materials for a user."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, file_name, file_path, uploaded_at
        FROM study_materials
        WHERE user_id = ?
        ORDER BY uploaded_at DESC
        """,
        (user_id,)
    )

    materials = cursor.fetchall()
    conn.close()

    return materials

create_tables() 