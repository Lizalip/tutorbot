from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
import enum
from database import Base


class UserRole(enum.Enum):
    """User role enumeration."""
    TUTOR = "tutor"
    STUDENT = "student"


class User(Base):
    """User model for storing tutor and student information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    name = Column(String(255))
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, name={self.name}, role={self.role.value})>"