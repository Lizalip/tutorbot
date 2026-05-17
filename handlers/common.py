from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import BUTTONS


def get_main_menu_keyboard(role: str = None):
    """Get main menu keyboard based on user role."""
    if role == "tutor":
        buttons = [
            [KeyboardButton(text=BUTTONS["lessons"])],
            [KeyboardButton(text=BUTTONS["add_lesson"])],
            [KeyboardButton(text=BUTTONS["homework"])],
            [KeyboardButton(text=BUTTONS["assign_homework"])],
            [KeyboardButton(text=BUTTONS["notes"])],
            [KeyboardButton(text=BUTTONS["add_note"])],
        ]
    else:  # student
        buttons = [
            [KeyboardButton(text=BUTTONS["lessons"])],
            [KeyboardButton(text=BUTTONS["homework"])],
        ]
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)


def get_role_selection_keyboard():
    """Get role selection keyboard."""
    buttons = [
        [KeyboardButton(text=BUTTONS["tutor"]), KeyboardButton(text=BUTTONS["student"])],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def get_yes_no_keyboard():
    """Get yes/no confirmation keyboard."""
    buttons = [
        [KeyboardButton(text=BUTTONS["yes"]), KeyboardButton(text=BUTTONS["no"])],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def get_back_cancel_keyboard():
    """Get back and cancel buttons."""
    buttons = [
        [KeyboardButton(text=BUTTONS["back"]), KeyboardButton(text=BUTTONS["cancel"])],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)


def get_lessons_inline_keyboard(lessons: list):
    """Get inline keyboard for lesson selection."""
    buttons = []
    for lesson in lessons:
        text = f"{lesson.subject} - {lesson.date.strftime('%d.%m %H:%M')}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"lesson_{lesson.id}")])
    
    buttons.append([InlineKeyboardButton(text=BUTTONS["back"], callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_homework_inline_keyboard(homework_list: list):
    """Get inline keyboard for homework selection."""
    buttons = []
    for hw in homework_list:
        text = f"{hw.subject} - {hw.due_date.strftime('%d.%m')}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"hw_{hw.id}")])
    
    buttons.append([InlineKeyboardButton(text=BUTTONS["back"], callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)