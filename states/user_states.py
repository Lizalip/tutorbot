from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    """User conversation states."""
    
    # Onboarding states
    WAITING_FOR_ROLE = State()
    WAITING_FOR_NAME = State()
    
    # Lesson states
    WAITING_FOR_LESSON_STUDENT = State()
    WAITING_FOR_LESSON_SUBJECT = State()
    WAITING_FOR_LESSON_DATE = State()
    WAITING_FOR_LESSON_TIME = State()
    WAITING_FOR_LESSON_DURATION = State()
    WAITING_FOR_LESSON_COMMENT = State()
    
    # Homework states
    WAITING_FOR_HOMEWORK_STUDENT = State()
    WAITING_FOR_HOMEWORK_SUBJECT = State()
    WAITING_FOR_HOMEWORK_DESCRIPTION = State()
    WAITING_FOR_HOMEWORK_DUE_DATE = State()
    WAITING_FOR_HOMEWORK_STATUS = State()
    WAITING_FOR_HOMEWORK_FEEDBACK = State()
    
    # Note states
    WAITING_FOR_NOTE_STUDENT = State()
    WAITING_FOR_NOTE_CONTENT = State()