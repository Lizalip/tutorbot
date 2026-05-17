"""
Database setup and simple queries.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE_FILE = "lessons.db"

def init_db():
    """Initialize database and create tables."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Lessons table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            lesson_date TEXT NOT NULL,
            lesson_time TEXT NOT NULL,
            comment TEXT,
            status TEXT DEFAULT 'planned',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(telegram_id)
        )
    """)
    
    conn.commit()
    conn.close()


def get_connection():
    """Get database connection."""
    return sqlite3.connect(DATABASE_FILE)


# ==================== USER FUNCTIONS ====================

def user_exists(telegram_id: int) -> bool:
    """Check if user exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def create_user(telegram_id: int, name: str, role: str) -> None:
    """Create new user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (telegram_id, name, role) VALUES (?, ?, ?)",
        (telegram_id, name, role)
    )
    conn.commit()
    conn.close()


def get_user_role(telegram_id: int) -> str:
    """Get user role."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_user_name(telegram_id: int) -> str:
    """Get user name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


# ==================== LESSON FUNCTIONS ====================

def create_lesson(student_id: int, subject: str, date: str, time: str, comment: str = None) -> int:
    """Create new lesson. Returns lesson ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO lessons (student_id, subject, lesson_date, lesson_time, comment)
           VALUES (?, ?, ?, ?, ?)""",
        (student_id, subject, date, time, comment)
    )
    lesson_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return lesson_id


def get_student_lessons(student_id: int) -> list:
    """Get all lessons for a student."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, subject, lesson_date, lesson_time, comment, status FROM lessons WHERE student_id = ? ORDER BY lesson_date DESC",
        (student_id,)
    )
    lessons = cursor.fetchall()
    conn.close()
    return lessons


def get_all_lesson_requests() -> list:
    """Get all lesson requests for tutors."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT l.id, u.name, l.subject, l.lesson_date, l.lesson_time, l.comment, l.status
           FROM lessons l
           JOIN users u ON l.student_id = u.telegram_id
           ORDER BY l.lesson_date DESC"""
    )
    lessons = cursor.fetchall()
    conn.close()
    return lessons


def get_lesson_by_id(lesson_id: int) -> tuple:
    """Get lesson details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT l.id, u.name, l.subject, l.lesson_date, l.lesson_time, l.comment, l.status
           FROM lessons l
           JOIN users u ON l.student_id = u.telegram_id
           WHERE l.id = ?""",
        (lesson_id,)
    )
    lesson = cursor.fetchone()
    conn.close()
    return lesson


def update_lesson_status(lesson_id: int, status: str) -> None:
    """Update lesson status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE lessons SET status = ? WHERE id = ?",
        (status, lesson_id)
    )
    conn.commit()
    conn.close()


def delete_lesson(lesson_id: int) -> None:
    """Delete lesson."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
    conn.commit()
    conn.close()