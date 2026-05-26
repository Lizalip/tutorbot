"""
Database setup and simple queries.
"""
import sqlite3

from config import TIME_SLOTS

DATABASE_FILE = "lessons.db"


def get_connection():
    """Get database connection."""
    return sqlite3.connect(DATABASE_FILE)


# ==================== HELPERS ====================

def normalize_text(value: str) -> str:
    """Strip extra spaces inside and outside a string."""
    return " ".join(value.strip().split())


def normalize_subjects_from_text(subjects_text: str) -> list[str]:
    """
    Convert comma-separated subjects text into a unique clean list.

    Example:
    "Математика, информатика, Математика"
    -> ["Математика", "информатика"]
    """
    raw_subjects = subjects_text.split(",")
    result = []
    seen = set()

    for subject in raw_subjects:
        clean_subject = normalize_text(subject)

        if not clean_subject:
            continue

        subject_key = clean_subject.lower()

        if subject_key not in seen:
            seen.add(subject_key)
            result.append(clean_subject)

    return result


def column_exists(cursor, table_name: str, column_name: str) -> bool:
    """Check whether a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(column[1] == column_name for column in columns)


# ==================== DATABASE INIT ====================

def init_db():
    """Initialize database, create tables, and run simple migrations."""
    conn = get_connection()
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

    # Tutor subjects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tutor_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tutor_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            FOREIGN KEY (tutor_id) REFERENCES users(telegram_id)
        )
    """)

    # Migration for an old lessons table without tutor_id
    if not column_exists(cursor, "lessons", "tutor_id"):
        cursor.execute("ALTER TABLE lessons ADD COLUMN tutor_id INTEGER")

    conn.commit()
    conn.close()


# ==================== DEBUG HELPER ====================

def debug_lessons_query() -> list:
    """
    Debug helper for developer testing.

    Shows lesson values in brackets to detect extra spaces.
    Do not expose this to bot users.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            id,
            '[' || COALESCE(CAST(tutor_id AS TEXT), '') || ']',
            '[' || subject || ']',
            '[' || lesson_date || ']',
            '[' || lesson_time || ']',
            '[' || status || ']'
        FROM lessons
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


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
        (telegram_id, normalize_text(name), role)
    )
    conn.commit()
    conn.close()


def get_user_role(telegram_id: int) -> str | None:
    """Get user role."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_user_name(telegram_id: int) -> str | None:
    """Get user name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


# ==================== TUTOR SUBJECT FUNCTIONS ====================

def save_tutor_subjects(tutor_id: int, subjects: list[str]) -> None:
    """Save tutor subjects without deleting existing subjects."""
    clean_subjects = []
    seen = set()

    for subject in subjects:
        clean_subject = normalize_text(subject)

        if not clean_subject:
            continue

        subject_key = clean_subject.lower()

        if subject_key not in seen:
            seen.add(subject_key)
            clean_subjects.append(clean_subject)

    if not clean_subjects:
        return

    conn = get_connection()
    cursor = conn.cursor()

    for subject in clean_subjects:
        cursor.execute(
            "INSERT INTO tutor_subjects (tutor_id, subject) VALUES (?, ?)",
            (tutor_id, subject)
        )

    conn.commit()
    conn.close()


def replace_tutor_subjects(tutor_id: int, subjects: list[str]) -> None:
    """Fully replace tutor's subjects."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tutor_subjects WHERE tutor_id = ?", (tutor_id,))

    conn.commit()
    conn.close()

    save_tutor_subjects(tutor_id, subjects)


def get_tutor_subjects(tutor_id: int) -> list[str]:
    """Get subjects of one tutor."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT subject
        FROM tutor_subjects
        WHERE tutor_id = ?
        ORDER BY subject
        """,
        (tutor_id,)
    )
    subjects = [row[0] for row in cursor.fetchall()]
    conn.close()
    return subjects


def get_all_unique_subjects() -> list[str]:
    """Get unique subjects from all tutors."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT subject FROM tutor_subjects ORDER BY subject")
    rows = cursor.fetchall()
    conn.close()

    result = []
    seen = set()

    for row in rows:
        subject = normalize_text(row[0])
        subject_key = subject.lower()

        if subject and subject_key not in seen:
            seen.add(subject_key)
            result.append(subject)

    return result


def get_tutors_by_subject(subject: str) -> list[tuple[int, str]]:
    """
    Get tutors who teach the selected subject.

    Returns:
        [(tutor_id, tutor_name), ...]
    """
    selected_subject = normalize_text(subject).lower()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.telegram_id, u.name, ts.subject
        FROM tutor_subjects ts
        JOIN users u ON ts.tutor_id = u.telegram_id
        WHERE u.role = 'tutor'
        ORDER BY u.name
    """)
    rows = cursor.fetchall()
    conn.close()

    result = []
    seen_tutors = set()

    for tutor_id, tutor_name, tutor_subject in rows:
        if normalize_text(tutor_subject).lower() == selected_subject:
            if tutor_id not in seen_tutors:
                seen_tutors.add(tutor_id)
                result.append((tutor_id, tutor_name))

    return result


# ==================== LESSON FUNCTIONS ====================

def is_slot_available(tutor_id: int, date: str, time: str) -> bool:
    """
    Check if a tutor's lesson slot is available.

    A slot is busy only if there is an existing lesson with:
    - same tutor_id
    - same date
    - same time
    - status = 'planned'

    Cancelled and completed lessons do not block the slot.
    """
    conn = get_connection()
    cursor = conn.cursor()

    date_normalized = normalize_text(date)
    time_normalized = normalize_text(time)

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM lessons
        WHERE tutor_id = ?
          AND TRIM(lesson_date) = ?
          AND TRIM(lesson_time) = ?
          AND TRIM(status) = 'planned'
        """,
        (tutor_id, date_normalized, time_normalized)
    )

    count = cursor.fetchone()[0]
    conn.close()

    return count == 0


def get_available_time_slots(tutor_id: int, date: str) -> list[str]:
    """Get available time slots for the selected tutor and date."""
    return [
        slot for slot in TIME_SLOTS
        if is_slot_available(tutor_id, date, slot)
    ]


def create_lesson(
    student_id: int,
    tutor_id: int,
    subject: str,
    date: str,
    time: str,
    comment: str | None = None
) -> int:
    """Create new lesson. Returns lesson ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO lessons (
            student_id,
            tutor_id,
            subject,
            lesson_date,
            lesson_time,
            comment,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, 'planned')
        """,
        (
            student_id,
            tutor_id,
            normalize_text(subject),
            normalize_text(date),
            normalize_text(time),
            normalize_text(comment) if comment else None
        )
    )

    lesson_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return lesson_id


def get_student_lessons(student_id: int) -> list:
    """
    Get all lessons for a student.

    Returns:
        id, subject, lesson_date, lesson_time, comment, status, tutor_name
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            l.id,
            l.subject,
            l.lesson_date,
            l.lesson_time,
            l.comment,
            l.status,
            COALESCE(t.name, 'Не указан') AS tutor_name
        FROM lessons l
        LEFT JOIN users t ON l.tutor_id = t.telegram_id
        WHERE l.student_id = ?
        ORDER BY l.lesson_date DESC, l.lesson_time DESC
        """,
        (student_id,)
    )

    lessons = cursor.fetchall()
    conn.close()

    return lessons


def get_all_lesson_requests() -> list:
    """
    Get all lesson requests for tutors.

    Returns:
        id, student_name, subject, lesson_date, lesson_time, comment, status, tutor_name
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            l.id,
            s.name AS student_name,
            l.subject,
            l.lesson_date,
            l.lesson_time,
            l.comment,
            l.status,
            COALESCE(t.name, 'Не указан') AS tutor_name
        FROM lessons l
        JOIN users s ON l.student_id = s.telegram_id
        LEFT JOIN users t ON l.tutor_id = t.telegram_id
        ORDER BY l.lesson_date DESC, l.lesson_time DESC
        """
    )

    lessons = cursor.fetchall()
    conn.close()

    return lessons


def get_tutor_lesson_requests(tutor_id: int) -> list:
    """
    Get lesson requests for one tutor.

    Returns:
        id, student_name, subject, lesson_date, lesson_time, comment, status, tutor_name
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            l.id,
            s.name AS student_name,
            l.subject,
            l.lesson_date,
            l.lesson_time,
            l.comment,
            l.status,
            COALESCE(t.name, 'Не указан') AS tutor_name
        FROM lessons l
        JOIN users s ON l.student_id = s.telegram_id
        LEFT JOIN users t ON l.tutor_id = t.telegram_id
        WHERE l.tutor_id = ?
        ORDER BY l.lesson_date DESC, l.lesson_time DESC
        """,
        (tutor_id,)
    )

    lessons = cursor.fetchall()
    conn.close()

    return lessons


def get_lesson_by_id(lesson_id: int) -> tuple | None:
    """
    Get lesson details.

    Returns:
        id, student_name, tutor_name, subject, lesson_date, lesson_time, comment, status
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            l.id,
            s.name AS student_name,
            COALESCE(t.name, 'Не указан') AS tutor_name,
            l.subject,
            l.lesson_date,
            l.lesson_time,
            l.comment,
            l.status
        FROM lessons l
        JOIN users s ON l.student_id = s.telegram_id
        LEFT JOIN users t ON l.tutor_id = t.telegram_id
        WHERE l.id = ?
        """,
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
    update_lesson_status(lesson_id, "cancelled")


def delete_lesson(lesson_id: int) -> None:
    """
    Physically delete lesson from database.

    Usually not needed for normal user cancellation.
    User cancellation should use cancel_lesson().
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))

    conn.commit()
    conn.close()