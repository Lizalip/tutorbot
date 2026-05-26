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
    
    # Tutor subjects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tutor_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tutor_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            FOREIGN KEY (tutor_id) REFERENCES users(telegram_id),
            UNIQUE(tutor_id, subject)
        )
    """)
    
    # Lessons table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            tutor_id INTEGER,
            subject TEXT NOT NULL,
            lesson_date TEXT NOT NULL,
            lesson_time TEXT NOT NULL,
            comment TEXT,
            status TEXT DEFAULT 'planned',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(telegram_id),
            FOREIGN KEY (tutor_id) REFERENCES users(telegram_id)
        )
    """)
    
    # Add tutor_id column if it's missing (migration)
    cursor.execute("PRAGMA table_info(lessons)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'tutor_id' not in columns:
        cursor.execute("ALTER TABLE lessons ADD COLUMN tutor_id INTEGER")
    
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


# ==================== TUTOR SUBJECTS FUNCTIONS ====================

def save_tutor_subjects(tutor_id: int, subjects: list[str]) -> None:
    """
    Save tutor subjects.
    Removes duplicates and normalizes subject names.
    """
    # Normalize and deduplicate subjects
    normalized_subjects = list(set(
        subject.strip() for subject in subjects if subject.strip()
    ))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Delete old subjects
    cursor.execute("DELETE FROM tutor_subjects WHERE tutor_id = ?", (tutor_id,))
    
    # Insert new subjects
    for subject in normalized_subjects:
        cursor.execute(
            "INSERT INTO tutor_subjects (tutor_id, subject) VALUES (?, ?)",
            (tutor_id, subject)
        )
    
    conn.commit()
    conn.close()


def replace_tutor_subjects(tutor_id: int, subjects: list[str]) -> None:
    """
    Replace tutor subjects.
    Fully replaces old subjects with new ones.
    """
    save_tutor_subjects(tutor_id, subjects)


def get_tutor_subjects(tutor_id: int) -> list[str]:
    """Get all subjects for a tutor."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT subject FROM tutor_subjects WHERE tutor_id = ? ORDER BY subject",
        (tutor_id,)
    )
    subjects = [row[0] for row in cursor.fetchall()]
    conn.close()
    return subjects


def get_all_unique_subjects() -> list[str]:
    """Get all unique subjects from all tutors."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT subject FROM tutor_subjects ORDER BY subject"
    )
    subjects = [row[0] for row in cursor.fetchall()]
    conn.close()
    return subjects


def get_tutors_by_subject(subject: str) -> list[tuple]:
    """
    Get all tutors who teach a given subject.
    Returns list of tuples: (tutor_id, tutor_name)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT u.telegram_id, u.name
           FROM users u
           JOIN tutor_subjects ts ON u.telegram_id = ts.tutor_id
           WHERE ts.subject = ? AND u.role = 'tutor'
           ORDER BY u.name""",
        (subject,)
    )
    tutors = cursor.fetchall()
    conn.close()
    return tutors


# ==================== TIME SLOT FUNCTIONS ====================

def get_available_time_slots(tutor_id: int, date: str) -> list[str]:
    """
    Get available time slots for a tutor on a given date.
    Returns list of time strings (HH:MM) from 08:00 to 21:00.
    Only slots without planned lessons are returned.
    """
    all_slots = [
        "08:00", "09:00", "10:00", "11:00", "12:00",
        "13:00", "14:00", "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00", "21:00"
    ]
    
    # Get busy slots
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT lesson_time FROM lessons
           WHERE tutor_id = ? AND lesson_date = ? AND status = 'planned'""",
        (tutor_id, date)
    )
    busy_times = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    # Return available slots
    return [slot for slot in all_slots if slot not in busy_times]


def is_slot_available(tutor_id: int, date: str, time: str) -> bool:
    """
    Check if a lesson slot is available.
    
    A slot is busy only if there is an existing lesson with:
    - same tutor_id
    - same date
    - same time
    - status = 'planned'
    
    Cancelled lessons do not block the slot.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT id FROM lessons
           WHERE tutor_id = ? AND lesson_date = ? AND lesson_time = ? AND status = 'planned'""",
        (tutor_id, date, time)
    )
    
    exists = cursor.fetchone() is not None
    conn.close()
    
    return not exists


# ==================== LESSON FUNCTIONS ====================

def create_lesson(student_id: int, tutor_id: int, subject: str, date: str, time: str, comment: str = None) -> int:
    """Create new lesson. Returns lesson ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO lessons (student_id, tutor_id, subject, lesson_date, lesson_time, comment, status)
           VALUES (?, ?, ?, ?, ?, ?, 'planned')""",
        (student_id, tutor_id, subject, date, time, comment)
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
        """SELECT l.id, u.name, l.subject, l.lesson_date, l.lesson_time, l.comment, l.status, l.tutor_id
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


def cancel_lesson(lesson_id: int) -> None:
    """Cancel lesson by updating status to 'cancelled'."""
    update_lesson_status(lesson_id, 'cancelled')
