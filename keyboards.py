"""
Keyboard layouts (buttons).
"""
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import BUTTONS


# ==================== REPLY KEYBOARDS ====================

def get_role_keyboard():
    """Role selection keyboard."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=BUTTONS["tutor"]),
                KeyboardButton(text=BUTTONS["student"]),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboard


def get_student_menu_keyboard():
    """Student main menu keyboard."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS["book_lesson"])],
            [KeyboardButton(text=BUTTONS["my_lessons"])],
            [KeyboardButton(text=BUTTONS["info"])],
            [KeyboardButton(text="/help")],
        ],
        resize_keyboard=True,
    )
    return keyboard


def get_tutor_menu_keyboard():
    """Tutor main menu keyboard."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS["view_requests"])],
            [KeyboardButton(text=BUTTONS["edit_subjects"])],
            [KeyboardButton(text="/help")],
        ],
        resize_keyboard=True,
    )
    return keyboard


def get_cancel_keyboard():
    """Keyboard with only cancel option."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS["cancel"])],
        ],
        resize_keyboard=True,
    )
    return keyboard


def get_skip_cancel_keyboard():
    """Keyboard with skip and cancel options for comment step."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS["skip"])],
            [KeyboardButton(text=BUTTONS["cancel"])],
        ],
        resize_keyboard=True,
    )
    return keyboard


# ==================== BOOKING INLINE KEYBOARDS ====================

def get_subjects_inline_keyboard(subjects: list[str]):
    """
    Inline keyboard for subject selection.

    Callback uses subject index instead of subject text:
    subject_0, subject_1, ...
    """
    buttons = []

    for index, subject in enumerate(subjects):
        buttons.append(
            [
                InlineKeyboardButton(
                    text=subject,
                    callback_data=f"subject_{index}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=BUTTONS["cancel"],
                callback_data="cancel_flow",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_tutors_inline_keyboard(tutors: list[tuple[int, str]]):
    """
    Inline keyboard for tutor selection.

    tutors format:
    [(tutor_id, tutor_name), ...]
    """
    buttons = []

    for tutor_id, tutor_name in tutors:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=tutor_name,
                    callback_data=f"tutor_{tutor_id}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=BUTTONS["cancel"],
                callback_data="cancel_flow",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_time_slots_inline_keyboard(slots: list[str]):
    """
    Inline keyboard for available time slots.

    Example:
    08:00 -> callback_data="time_08_00"
    """
    buttons = []

    row = []
    for slot in slots:
        callback_time = slot.replace(":", "_")

        row.append(
            InlineKeyboardButton(
                text=slot,
                callback_data=f"time_{callback_time}",
            )
        )

        # Two buttons per row for compact layout
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append(
        [
            InlineKeyboardButton(
                text=BUTTONS["cancel"],
                callback_data="cancel_flow",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_booking_confirmation_keyboard():
    """Inline keyboard for booking confirmation."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=BUTTONS["confirm"],
                    callback_data="confirm_booking",
                )
            ],
            [
                InlineKeyboardButton(
                    text=BUTTONS["change"],
                    callback_data="change_booking",
                )
            ],
            [
                InlineKeyboardButton(
                    text=BUTTONS["cancel_booking"],
                    callback_data="cancel_booking",
                )
            ],
        ]
    )
    return keyboard


# ==================== LESSON INLINE KEYBOARDS ====================

def get_lessons_inline_keyboard(lessons: list, callback_prefix: str = "lesson"):
    """
    Inline keyboard for lesson/request selection.

    Student lessons format:
    id, subject, lesson_date, lesson_time, comment, status, tutor_name

    Tutor requests format:
    id, student_name, subject, lesson_date, lesson_time, comment, status, tutor_name
    """
    buttons = []

    for lesson in lessons:
        lesson_id = lesson[0]
        callback_data = f"{callback_prefix}_{lesson_id}"

        if callback_prefix == "request":
            # Tutor request:
            # id, student_name, subject, lesson_date, lesson_time, comment, status, tutor_name
            student_name = lesson[1]
            subject = lesson[2]
            lesson_date = lesson[3]
            lesson_time = lesson[4]
            text = f"{student_name[:18]} — {subject[:18]} — {lesson_date} {lesson_time}"
        else:
            # Student lesson:
            # id, subject, lesson_date, lesson_time, comment, status, tutor_name
            subject = lesson[1]
            lesson_date = lesson[2]
            lesson_time = lesson[3]
            text = f"{subject[:25]} — {lesson_date} {lesson_time}"

        buttons.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data,
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lesson_actions_keyboard(lesson_id: int):
    """Inline keyboard for student lesson actions."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=BUTTONS["cancel_lesson"],
                    callback_data=f"cancel_student_{lesson_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=BUTTONS["back"],
                    callback_data="back_to_menu",
                )
            ],
        ]
    )
    return keyboard


def get_tutor_lesson_actions_keyboard(lesson_id: int):
    """Inline keyboard for tutor lesson actions."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=BUTTONS["planned"],
                    callback_data=f"status_{lesson_id}_planned",
                )
            ],
            [
                InlineKeyboardButton(
                    text=BUTTONS["completed"],
                    callback_data=f"status_{lesson_id}_completed",
                )
            ],
            [
                InlineKeyboardButton(
                    text=BUTTONS["cancelled"],
                    callback_data=f"status_{lesson_id}_cancelled",
                )
            ],
            [
                InlineKeyboardButton(
                    text=BUTTONS["back"],
                    callback_data="back_to_menu",
                )
            ],
        ]
    )
    return keyboard