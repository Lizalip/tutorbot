from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from datetime import datetime
import enum
from database import Base


class HomeworkStatus(enum.Enum):
    """Homework status enumeration."""
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    CHECKED = "checked"


class Homework(Base):
    """Homework model for storing homework assignments."""
    __tablename__ = "homework"

    id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(HomeworkStatus), default=HomeworkStatus.ASSIGNED)
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Homework(subject={self.subject}, status={self.status.value})>"