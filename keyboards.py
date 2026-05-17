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
            [KeyboardButton(text="/help")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_skip_keyboard():
    """Keyboard with skip option."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS["skip"])],
            [KeyboardButton(text=BUTTONS["cancel"])]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_lessons_inline_keyboard(lessons: list, callback_prefix: str = "lesson"):
    """Inline keyboard for lesson selection."""
    buttons = []
    for lesson in lessons:
        callback_data = f"{callback_prefix}_{lesson[0]}"
        text = f"{lesson[1][:30]} - {lesson[2]} {lesson[3]}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lesson_actions_keyboard(lesson_id: int):
    """Keyboard for lesson actions (student or tutor)."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=BUTTONS["delete"], callback_data=f"delete_{lesson_id}")],
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