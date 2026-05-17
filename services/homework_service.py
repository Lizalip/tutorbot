from sqlalchemy.orm import Session
from datetime import datetime
from models.homework import Homework, HomeworkStatus
from database import get_session


class HomeworkService:
    """Service for managing homework operations."""

    @staticmethod
    def assign_homework(tutor_id: int, student_id: int, subject: str,
                       description: str, due_date: datetime, session: Session = None):
        """Assign homework to a student."""
        if session is None:
            session = get_session()
        
        homework = Homework(
            tutor_id=tutor_id,
            student_id=student_id,
            subject=subject,
            description=description,
            due_date=due_date
        )
        session.add(homework)
        session.commit()
        session.refresh(homework)
        return homework

    @staticmethod
    def get_homework(homework_id: int, session: Session = None):
        """Get homework by ID."""
        if session is None:
            session = get_session()
        
        return session.query(Homework).filter(
            Homework.id == homework_id
        ).first()

    @staticmethod
    def get_student_homework(student_id: int, status: HomeworkStatus = None, session: Session = None):
        """Get all homework for a student."""
        if session is None:
            session = get_session()
        
        query = session.query(Homework).filter(
            Homework.student_id == student_id
        )
        
        if status:
            query = query.filter(Homework.status == status)
        
        return query.order_by(Homework.due_date).all()

    @staticmethod
    def get_tutor_homework(tutor_id: int, status: HomeworkStatus = None, session: Session = None):
        """Get all homework assigned by a tutor."""
        if session is None:
            session = get_session()
        
        query = session.query(Homework).filter(
            Homework.tutor_id == tutor_id
        )
        
        if status:
            query = query.filter(Homework.status == status)
        
        return query.order_by(Homework.due_date).all()

    @staticmethod
    def update_homework_status(homework_id: int, status: HomeworkStatus, 
                              feedback: str = None, session: Session = None):
        """Update homework status."""
        if session is None:
            session = get_session()
        
        homework = session.query(Homework).filter(
            Homework.id == homework_id
        ).first()
        
        if homework:
            homework.status = status
            if feedback:
                homework.feedback = feedback
            session.commit()
            session.refresh(homework)
        
        return homework

    @staticmethod
    def delete_homework(homework_id: int, session: Session = None):
        """Delete homework."""
        if session is None:
            session = get_session()
        
        homework = session.query(Homework).filter(
            Homework.id == homework_id
        ).first()
        
        if homework:
            session.delete(homework)
            session.commit()
            return True
        
        return False