from sqlalchemy.orm import Session
from models.note import Note
from database import get_session


class NoteService:
    """Service for managing note operations."""

    @staticmethod
    def create_note(tutor_id: int, student_id: int, content: str,
                   lesson_id: int = None, session: Session = None):
        """Create a new note."""
        if session is None:
            session = get_session()
        
        note = Note(
            tutor_id=tutor_id,
            student_id=student_id,
            content=content,
            lesson_id=lesson_id
        )
        session.add(note)
        session.commit()
        session.refresh(note)
        return note

    @staticmethod
    def get_note(note_id: int, session: Session = None):
        """Get note by ID."""
        if session is None:
            session = get_session()
        
        return session.query(Note).filter(
            Note.id == note_id
        ).first()

    @staticmethod
    def get_tutor_student_notes(tutor_id: int, student_id: int, session: Session = None):
        """Get all notes from tutor about a student."""
        if session is None:
            session = get_session()
        
        return session.query(Note).filter(
            Note.tutor_id == tutor_id,
            Note.student_id == student_id
        ).order_by(Note.created_at.desc()).all()

    @staticmethod
    def get_all_tutor_notes(tutor_id: int, session: Session = None):
        """Get all notes from a tutor."""
        if session is None:
            session = get_session()
        
        return session.query(Note).filter(
            Note.tutor_id == tutor_id
        ).order_by(Note.created_at.desc()).all()

    @staticmethod
    def update_note(note_id: int, content: str, session: Session = None):
        """Update note content."""
        if session is None:
            session = get_session()
        
        note = session.query(Note).filter(
            Note.id == note_id
        ).first()
        
        if note:
            note.content = content
            session.commit()
            session.refresh(note)
        
        return note

    @staticmethod
    def delete_note(note_id: int, session: Session = None):
        """Delete a note."""
        if session is None:
            session = get_session()
        
        note = session.query(Note).filter(
            Note.id == note_id
        ).first()
        
        if note:
            session.delete(note)
            session.commit()
            return True
        
        return False