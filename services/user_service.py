from sqlalchemy.orm import Session
from models.user import User, UserRole
from database import get_session


class UserService:
    """Service for managing user operations."""

    @staticmethod
    def create_user(telegram_id: int, name: str, role: UserRole, session: Session = None):
        """Create a new user."""
        if session is None:
            session = get_session()
        
        # Check if user already exists
        existing_user = session.query(User).filter(
            User.telegram_id == telegram_id
        ).first()
        
        if existing_user:
            return existing_user
        
        user = User(
            telegram_id=telegram_id,
            name=name,
            role=role
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @staticmethod
    def get_user(telegram_id: int, session: Session = None):
        """Get user by telegram_id."""
        if session is None:
            session = get_session()
        
        return session.query(User).filter(
            User.telegram_id == telegram_id
        ).first()

    @staticmethod
    def get_user_by_name(name: str, session: Session = None):
        """Get user by name."""
        if session is None:
            session = get_session()
        
        return session.query(User).filter(
            User.name.ilike(f"%{name}%")
        ).first()

    @staticmethod
    def get_all_tutors(session: Session = None):
        """Get all tutors."""
        if session is None:
            session = get_session()
        
        return session.query(User).filter(
            User.role == UserRole.TUTOR
        ).all()

    @staticmethod
    def get_all_students(session: Session = None):
        """Get all students."""
        if session is None:
            session = get_session()
        
        return session.query(User).filter(
            User.role == UserRole.STUDENT
        ).all()

    @staticmethod
    def update_user_name(telegram_id: int, name: str, session: Session = None):
        """Update user name."""
        if session is None:
            session = get_session()
        
        user = session.query(User).filter(
            User.telegram_id == telegram_id
        ).first()
        
        if user:
            user.name = name
            session.commit()
            session.refresh(user)
        
        return user