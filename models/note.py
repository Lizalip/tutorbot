from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from database import Base


class Note(Base):
    """Note model for storing tutor notes about lessons."""
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Note(tutor_id={self.tutor_id}, student_id={self.student_id})>"