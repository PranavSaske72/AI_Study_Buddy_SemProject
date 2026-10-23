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

def create_quiz(user_id, title, subject="General"):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO quizzes (user_id, title, subject)
            VALUES (?, ?, ?)
        """, (user_id, title, subject))

        quiz_id = cursor.lastrowid
        conn.commit()
        return quiz_id

    finally:
        conn.close()


def save_quiz_questions(quiz_id, questions):
    import json

    conn = get_connection()
    cursor = conn.cursor()

    try:
        for item in questions:
            cursor.execute("""
                INSERT INTO quiz_questions
                (quiz_id, question, options, correct_answer, explanation)
                VALUES (?, ?, ?, ?, ?)
            """, (
                quiz_id,
                item["question"],
                json.dumps(item["options"]),
                item["correct_answer"],
                item.get("explanation", "")
            ))

        conn.commit()

    finally:
        conn.close()


def get_quiz_questions(quiz_id):
    import json

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, question, options, explanation
            FROM quiz_questions
            WHERE quiz_id = ?
        """, (quiz_id,))

        questions = cursor.fetchall()

        return [
            {
                "id": row[0],
                "question": row[1],
                "options": json.loads(row[2]),
                "explanation": row[3]
            }
            for row in questions
        ]

    finally:
        conn.close()


def save_quiz_attempt(user_id, quiz_id, score, total_questions):
    if total_questions <= 0:
        raise ValueError("Total questions must be greater than zero.")

    if not 0 <= score <= total_questions:
        raise ValueError("Score must be between zero and total questions.")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO quiz_attempts
            (user_id, quiz_id, score, total_questions)
            SELECT ?, id, ?, ?
            FROM quizzes
            WHERE id = ? AND user_id = ?
        """, (
            user_id, score, total_questions, quiz_id, user_id
        ))

        if cursor.rowcount != 1:
            raise ValueError("Quiz not found for this user.")

        conn.commit()

    finally:
        conn.close()


def get_quiz_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                q.title,
                q.subject,
                a.score,
                a.total_questions,
                a.attempted_at
            FROM quiz_attempts AS a
            JOIN quizzes AS q ON q.id = a.quiz_id
            WHERE a.user_id = ? AND q.user_id = ?
            ORDER BY a.attempted_at DESC
        """, (user_id, user_id))

        return cursor.fetchall()

    finally:
        conn.close()

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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            subject TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            duration_minutes INTEGER DEFAULT 0,
            activity_date DATE DEFAULT CURRENT_DATE,
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

def get_dashboard_stats(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM study_materials
            WHERE user_id = ?
        """, (user_id,))
        materials_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT
                COUNT(*),
                COALESCE(
                    AVG(100.0 * score / total_questions), 0
                )
            FROM quiz_attempts
            WHERE user_id = ? AND total_questions > 0
        """, (user_id,))
        quizzes_taken, avg_score = cursor.fetchone()

        cursor.execute("""
            SELECT COALESCE(SUM(duration_minutes), 0)
            FROM study_activity
            WHERE user_id = ?
        """, (user_id,))
        study_minutes = cursor.fetchone()[0]

        return {
            "materials_count": materials_count,
            "study_minutes": study_minutes,
            "quizzes_taken": quizzes_taken,
            "avg_score": avg_score,
            "day_streak": get_study_streak(user_id),
        }

    finally:
        conn.close()


def get_quiz_activity(user_id, days=7):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT date(attempted_at), COUNT(*)
            FROM quiz_attempts
            WHERE user_id = ?
              AND date(attempted_at) >= date('now', ?)
            GROUP BY date(attempted_at)
            ORDER BY date(attempted_at)
        """, (user_id, f"-{max(1, days - 1)} days"))

        return cursor.fetchall()

    finally:
        conn.close()


def get_topic_distribution(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                COALESCE(q.subject, 'General'),
                COUNT(a.id)
            FROM quiz_attempts AS a
            JOIN quizzes AS q ON q.id = a.quiz_id
            WHERE a.user_id = ? AND q.user_id = ?
            GROUP BY COALESCE(q.subject, 'General')
            ORDER BY COUNT(a.id) DESC
        """, (user_id, user_id))

        return cursor.fetchall()

    finally:
        conn.close()


def get_study_streak(user_id):
    from datetime import date, timedelta

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT date(activity_date)
            FROM study_activity
            WHERE user_id = ?

            UNION

            SELECT date(attempted_at)
            FROM quiz_attempts
            WHERE user_id = ?
        """, (user_id, user_id))

        active_dates = {
            row[0] for row in cursor.fetchall() if row[0]
        }

        today = date.today()
        current_date = today.isoformat()

        # If there was no activity today, allow the streak
        # to continue from yesterday.
        if current_date not in active_dates:
            current_date = (today - timedelta(days=1)).isoformat()

        streak = 0

        while current_date in active_dates:
            streak += 1
            current_date = (
                date.fromisoformat(current_date)
                - timedelta(days=1)
            ).isoformat()

        return streak

    finally:
        conn.close()

def get_analytics_data(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                date(a.attempted_at) AS date,
                0 AS duration_minutes,
                100.0 * a.score / a.total_questions AS score,
                COALESCE(q.subject, 'General') AS topic
            FROM quiz_attempts AS a
            JOIN quizzes AS q ON q.id = a.quiz_id
            WHERE a.user_id = ?
              AND q.user_id = ?
              AND a.total_questions > 0
            ORDER BY a.attempted_at
        """, (user_id, user_id))

        rows = cursor.fetchall()

        return [
            {
                "date": row[0],
                "duration_minutes": row[1],
                "score": row[2],
                "topic": row[3],
            }
            for row in rows
        ]

    finally:
        conn.close()

def save_study_activity(
    user_id,
    activity_type,
    duration_minutes=0
):
    if duration_minutes < 0:
        raise ValueError("Duration cannot be negative.")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO study_activity
            (user_id, activity_type, duration_minutes)
            VALUES (?, ?, ?)
        """, (
            user_id,
            activity_type,
            duration_minutes
        ))

        conn.commit()

    finally:
        conn.close()

create_tables() 