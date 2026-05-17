from sqlalchemy.orm import Session
from datetime import datetime
from models.lesson import Lesson, LessonStatus
from database import get_session


class LessonService:
    """Service for managing lesson operations."""

    @staticmethod
    def create_lesson(tutor_id: int, student_id: int, subject: str, 
                     date: datetime, duration_minutes: int = 60, 
                     comment: str = None, session: Session = None):
        """Create a new lesson."""
        if session is None:
            session = get_session()
        
        lesson = Lesson(
            tutor_id=tutor_id,
            student_id=student_id,
            subject=subject,
            date=date,
            duration_minutes=duration_minutes,
            comment=comment
        )
        session.add(lesson)
        session.commit()
        session.refresh(lesson)
        return lesson

    @staticmethod
    def get_lesson(lesson_id: int, session: Session = None):
        """Get lesson by ID."""
        if session is None:
            session = get_session()
        
        return session.query(Lesson).filter(
            Lesson.id == lesson_id
        ).first()

    @staticmethod
    def get_tutor_lessons(tutor_id: int, status: LessonStatus = None, session: Session = None):
        """Get all lessons for a tutor."""
        if session is None:
            session = get_session()
        
        query = session.query(Lesson).filter(
            Lesson.tutor_id == tutor_id
        )
        
        if status:
            query = query.filter(Lesson.status == status)
        
        return query.order_by(Lesson.date).all()

    @staticmethod
    def get_student_lessons(student_id: int, status: LessonStatus = None, session: Session = None):
        """Get all lessons for a student."""
        if session is None:
            session = get_session()
        
        query = session.query(Lesson).filter(
            Lesson.student_id == student_id
        )
        
        if status:
            query = query.filter(Lesson.status == status)
        
        return query.order_by(Lesson.date).all()

    @staticmethod
    def update_lesson_status(lesson_id: int, status: LessonStatus, session: Session = None):
        """Update lesson status."""
        if session is None:
            session = get_session()
        
        lesson = session.query(Lesson).filter(
            Lesson.id == lesson_id
        ).first()
        
        if lesson:
            lesson.status = status
            session.commit()
            session.refresh(lesson)
        
        return lesson

    @staticmethod
    def delete_lesson(lesson_id: int, session: Session = None):
        """Delete a lesson."""
        if session is None:
            session = get_session()
        
        lesson = session.query(Lesson).filter(
            Lesson.id == lesson_id
        ).first()
        
        if lesson:
            session.delete(lesson)
            session.commit()
            return True
        
        return False

    @staticmethod
    def get_upcoming_lessons(minutes_until: int = 60, session: Session = None):
        """Get lessons happening in the next N minutes."""
        if session is None:
            session = get_session()
        
        now = datetime.utcnow()
        from datetime import timedelta
        future = now + timedelta(minutes=minutes_until)
        
        return session.query(Lesson).filter(
            Lesson.date >= now,
            Lesson.date <= future,
            Lesson.status == LessonStatus.SCHEDULED
        ).all()