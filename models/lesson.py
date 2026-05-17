from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from datetime import datetime
import enum
from database import Base


class LessonStatus(enum.Enum):
    """Lesson status enumeration."""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Lesson(Base):
    """Lesson model for storing lesson information."""
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    subject = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    comment = Column(Text)
    status = Column(Enum(LessonStatus), default=LessonStatus.SCHEDULED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Lesson(subject={self.subject}, date={self.date}, status={self.status.value})>"