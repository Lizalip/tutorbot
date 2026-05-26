"""
Keyboard layouts (buttons).
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import BUTTONS, STATUS_NAMES


def get_role_keyboard():
    """Role selection keyboard."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS["tutor"]), KeyboardButton(text=BUTTONS["student"])]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_student_menu_keyboard():
    """Student main menu keyboard."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS["book_lesson"])],
            [KeyboardButton(text=BUTTONS["my_lessons"])],
            [KeyboardButton(text=BUTTONS["info"])],
            [KeyboardButton(text="/help")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_tutor_menu_keyboard():
    """Tutor main menu keyboard."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS["view_requests"])],
            [KeyboardButton(text=BUTTONS["edit_subjects"])],
            [KeyboardButton(text="/help")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_cancel_keyboard():
    """Keyboard with only cancel option (for subject, date, time)."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS["cancel"])]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_skip_cancel_keyboard():
    """Keyboard with skip and cancel options (for comment step)."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS["skip"])],
            [KeyboardButton(text=BUTTONS["cancel"])]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_booking_confirmation_keyboard():
    """Keyboard for booking confirmation."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=BUTTONS["confirm"], callback_data="confirm_booking")],
            [InlineKeyboardButton(text=BUTTONS["change"], callback_data="change_booking")],
            [InlineKeyboardButton(text=BUTTONS["cancel_booking"], callback_data="cancel_booking")]
        ]
    )
    return keyboard


def get_subjects_inline_keyboard(subjects: list[str]):
    """Inline keyboard for subject selection."""
    buttons = []
    for idx, subject in enumerate(subjects):
        callback_data = f"subject_{idx}"
        buttons.append([InlineKeyboardButton(text=subject, callback_data=callback_data)])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_tutors_inline_keyboard(tutors: list[tuple]):
    """Inline keyboard for tutor selection."""
    buttons = []
    for tutor_id, tutor_name in tutors:
        callback_data = f"tutor_{tutor_id}"
        buttons.append([InlineKeyboardButton(text=tutor_name, callback_data=callback_data)])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_time_slots_inline_keyboard(slots: list[str]):
    """Inline keyboard for time slot selection."""
    buttons = []
    # Create a 2-column layout for time slots
    for i in range(0, len(slots), 2):
        row = []
        for j in range(2):
            if i + j < len(slots):
                slot = slots[i + j]
                callback_data = f"time_{slot.replace(':', '_')}"
                row.append(InlineKeyboardButton(text=slot, callback_data=callback_data))
        if row:
            buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lessons_inline_keyboard(lessons: list, callback_prefix: str = "lesson"):
    """Inline keyboard for lesson selection."""
    buttons = []
    for lesson in lessons:
        callback_data = f"{callback_prefix}_{lesson[0]}"
        text = f"{lesson[1][:30]} - {lesson[2]} {lesson[3]}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lesson_actions_keyboard(lesson_id: int):
    """Keyboard for lesson actions (student)."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=BUTTONS["cancel_lesson"], callback_data=f"cancel_student_{lesson_id}")],
            [InlineKeyboardButton(text=BUTTONS["back"], callback_data="back_to_menu")]
        ]
    )
    return keyboard


def get_tutor_lesson_actions_keyboard(lesson_id: int):
    """Keyboard for tutor lesson actions."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=BUTTONS["planned"], callback_data=f"status_{lesson_id}_planned")],
            [InlineKeyboardButton(text=BUTTONS["completed"], callback_data=f"status_{lesson_id}_completed")],
            [InlineKeyboardButton(text=BUTTONS["cancelled"], callback_data=f"status_{lesson_id}_cancelled")],
            [InlineKeyboardButton(text=BUTTONS["back"], callback_data="back_to_menu")]
        ]
    )
    return keyboard
