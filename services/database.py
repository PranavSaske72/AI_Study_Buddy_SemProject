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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            study_goal INTEGER DEFAULT 90,
            difficulty TEXT DEFAULT 'Medium',
            favorite_subject TEXT DEFAULT 'Mathematics',
            notifications INTEGER DEFAULT 1,
            quiz_notifications INTEGER DEFAULT 1,
            theme TEXT DEFAULT 'Light',
            ai_model TEXT DEFAULT 'gemini-3.5-flash-lite',
            ai_tone TEXT DEFAULT 'Friendly & Clear',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password):
    """Convert a password into a secure hash."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(name, email, password):
    """Create a new user account. Returns (success, user_id, message)."""
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

        user_id = cursor.lastrowid
        conn.commit()
        return True, user_id, "Account created successfully."

    except sqlite3.IntegrityError:
        return False, None, "An account with this email already exists."

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


def get_user_by_id(user_id):
    """Fetch user by id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "email": row[2]}
    return None


def update_user_profile(user_id, name, email):
    """Update user's name and email."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (name, email, user_id)
        )
        conn.commit()
        return True, "Profile updated successfully."
    except sqlite3.IntegrityError:
        return False, "This email is already in use by another account."
    finally:
        conn.close()


def update_user_password(user_id, old_password, new_password):
    """Update password after verifying old password."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return False, "User not found."
        
        if row[0] != hash_password(old_password):
            return False, "Current password is incorrect."
        
        cursor.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (hash_password(new_password), user_id)
        )
        conn.commit()
        return True, "Password changed successfully."
    finally:
        conn.close()


def get_user_settings(user_id):
    """Retrieve user settings dictionary."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT study_goal, difficulty, favorite_subject, notifications, quiz_notifications, theme, ai_model, ai_tone
            FROM user_settings WHERE user_id = ?
            """,
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "study_goal": row[0],
                "difficulty": row[1],
                "favorite_subject": row[2],
                "notifications": bool(row[3]),
                "quiz_notifications": bool(row[4]),
                "theme": row[5],
                "ai_model": row[6],
                "ai_tone": row[7]
            }
        else:
            return {
                "study_goal": 90,
                "difficulty": "Medium",
                "favorite_subject": "Mathematics",
                "notifications": True,
                "quiz_notifications": True,
                "theme": "Light",
                "ai_model": "gemini-3.5-flash-lite",
                "ai_tone": "Friendly & Clear"
            }
    finally:
        conn.close()


def save_user_settings(user_id, settings):
    """Save or update user settings dictionary."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO user_settings (user_id, study_goal, difficulty, favorite_subject, notifications, quiz_notifications, theme, ai_model, ai_tone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                study_goal=excluded.study_goal,
                difficulty=excluded.difficulty,
                favorite_subject=excluded.favorite_subject,
                notifications=excluded.notifications,
                quiz_notifications=excluded.quiz_notifications,
                theme=excluded.theme,
                ai_model=excluded.ai_model,
                ai_tone=excluded.ai_tone
            """,
            (
                user_id,
                settings.get("study_goal", 90),
                settings.get("difficulty", "Medium"),
                settings.get("favorite_subject", "Mathematics"),
                1 if settings.get("notifications", True) else 0,
                1 if settings.get("quiz_notifications", True) else 0,
                settings.get("theme", "Light"),
                settings.get("ai_model", "gemini-3.8-flash"),
                settings.get("ai_tone", "Friendly & Clear")
            )
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_or_create_dev_user():
    """Ensure a default dev account exists and return its (id, name, email)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, email FROM users WHERE email = 'alex@studyhub.ai'")
        row = cursor.fetchone()
        if row:
            return row[0], row[1], row[2]
        
        # Create a default user if none exists
        pwd_hash = hash_password("student123")
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ("Alex Morgan", "alex@studyhub.ai", pwd_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        return user_id, "Alex Morgan", "alex@studyhub.ai"
    finally:
        conn.close()


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


def delete_study_material(material_id, user_id):
    """Delete a study material entry for a user and remove its local file."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT file_path FROM study_materials WHERE id = ? AND user_id = ?", (material_id, user_id))
        row = cursor.fetchone()
        if row and row[0]:
            try:
                p = Path(row[0])
                if p.exists():
                    p.unlink(missing_ok=True)
                txt_p = Path(f"{row[0]}.txt")
                if txt_p.exists():
                    txt_p.unlink(missing_ok=True)
            except Exception:
                pass
        cursor.execute("DELETE FROM study_materials WHERE id = ? AND user_id = ?", (material_id, user_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


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