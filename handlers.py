"""
Command and message handlers.
"""
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import re

from config import MESSAGES, BUTTONS, STATUS_NAMES
from database import (
    user_exists, create_user, get_user_role, get_user_name,
    create_lesson, get_student_lessons, get_all_lesson_requests,
    get_lesson_by_id, update_lesson_status, cancel_lesson, is_slot_available
)
from keyboards import (
    get_role_keyboard, get_student_menu_keyboard, get_tutor_menu_keyboard,
    get_cancel_keyboard, get_skip_cancel_keyboard, get_lessons_inline_keyboard,
    get_lesson_actions_keyboard, get_tutor_lesson_actions_keyboard,
    get_booking_confirmation_keyboard
)

router = Router()


# ==================== FSM STATES ====================

class UserStates(StatesGroup):
    """States for user conversation flow."""
    waiting_for_role = State()
    waiting_for_name = State()
    booking_subject = State()
    booking_date = State()
    booking_time = State()
    booking_comment = State()
    booking_confirm = State()


# ==================== HELPER FUNCTIONS ====================

async def cancel_current_action(message: types.Message, state: FSMContext) -> None:
    """
    Cancel the current unfinished FSM scenario.
    Clear state and return user to appropriate menu.
    """
    await state.clear()
    
    if not user_exists(message.from_user.id):
        # User not registered yet
        await message.answer(MESSAGES["welcome"], reply_markup=get_role_keyboard())
        await state.set_state(UserStates.waiting_for_role)
    else:
        # User is registered, show appropriate menu
        role = get_user_role(message.from_user.id)
        if role == "tutor":
            await message.answer(MESSAGES["main_menu_tutor"], reply_markup=get_tutor_menu_keyboard())
        else:
            await message.answer(MESSAGES["main_menu_student"], reply_markup=get_student_menu_keyboard())


# ==================== START & HELP & INFO ====================

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Handle /start command."""
    if user_exists(message.from_user.id):
        # User already registered
        role = get_user_role(message.from_user.id)
        if role == "tutor":
            await message.answer(MESSAGES["main_menu_tutor"], reply_markup=get_tutor_menu_keyboard())
        else:
            await message.answer(MESSAGES["main_menu_student"], reply_markup=get_student_menu_keyboard())
    else:
        # New user - ask for role
        await message.answer(MESSAGES["welcome"], reply_markup=get_role_keyboard())
        await state.set_state(UserStates.waiting_for_role)


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handle /help command."""
    await message.answer(MESSAGES["help"])


@router.message(Command("info"))
async def cmd_info(message: types.Message):
    """Handle /info command."""
    await message.answer(MESSAGES["info"])


@router.message(Command("menu"))
async def cmd_menu(message: types.Message):
    """Handle /menu command."""
    if not user_exists(message.from_user.id):
        await message.answer(MESSAGES["error"])
        return
    
    role = get_user_role(message.from_user.id)
    if role == "tutor":
        await message.answer(MESSAGES["main_menu_tutor"], reply_markup=get_tutor_menu_keyboard())
    else:
        await message.answer(MESSAGES["main_menu_student"], reply_markup=get_student_menu_keyboard())


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Handle /cancel command - cancel unfinished scenario."""
    current_state = await state.get_state()
    
    if current_state:
        # There is an active FSM state
        await message.answer(MESSAGES["current_action_cancelled"])
        await cancel_current_action(message, state)
    else:
        # No active FSM state
        await message.answer(MESSAGES["no_active_action"])
        
        if user_exists(message.from_user.id):
            role = get_user_role(message.from_user.id)
            if role == "tutor":
                await message.answer(MESSAGES["main_menu_tutor"], reply_markup=get_tutor_menu_keyboard())
            else:
                await message.answer(MESSAGES["main_menu_student"], reply_markup=get_student_menu_keyboard())


# ==================== ROLE SELECTION & NAME ====================

@router.message(UserStates.waiting_for_role, F.text == BUTTONS["tutor"])
async def choose_tutor(message: types.Message, state: FSMContext):
    """User chooses tutor role."""
    await state.update_data(role="tutor")
    await message.answer(MESSAGES["ask_name"])
    await state.set_state(UserStates.waiting_for_name)


@router.message(UserStates.waiting_for_role, F.text == BUTTONS["student"])
async def choose_student(message: types.Message, state: FSMContext):
    """User chooses student role."""
    await state.update_data(role="student")
    await message.answer(MESSAGES["ask_name"])
    await state.set_state(UserStates.waiting_for_name)


@router.message(UserStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Process user name."""
    name = message.text.strip()
    if not name or len(name) < 2:
        await message.answer(MESSAGES["invalid_input"])
        return
    
    data = await state.get_data()
    role = data["role"]
    
    # Save to database
    create_user(message.from_user.id, name, role)
    
    # Show role confirmation
    role_display = "Преподаватель" if role == "tutor" else "Студент"
    await message.answer(MESSAGES["role_selected"].format(role_display))
    
    # Show appropriate menu
    if role == "tutor":
        await message.answer(MESSAGES["main_menu_tutor"], reply_markup=get_tutor_menu_keyboard())
    else:
        await message.answer(MESSAGES["main_menu_student"], reply_markup=get_student_menu_keyboard())
    
    await state.clear()


# ==================== STUDENT: BOOK LESSON ====================

@router.message(F.text == BUTTONS["book_lesson"])
async def book_lesson_start(message: types.Message, state: FSMContext):
    """Start lesson booking."""
    if not user_exists(message.from_user.id):
        await message.answer(MESSAGES["error"])
        return
    
    if get_user_role(message.from_user.id) != "student":
        await message.answer("❌ Только студенты могут записаться на урок")
        return
    
    await message.answer(MESSAGES["ask_subject"], reply_markup=get_cancel_keyboard())
    await state.set_state(UserStates.booking_subject)


@router.message(UserStates.booking_subject)
async def booking_subject(message: types.Message, state: FSMContext):
    """Process subject."""
    if message.text == BUTTONS["cancel"]:
        await cancel_current_action(message, state)
        return
    
    # Normalize subject: strip whitespace
    subject = message.text.strip()
    if not subject:
        await message.answer(MESSAGES["invalid_input"])
        return
    
    await state.update_data(subject=subject)
    await message.answer(MESSAGES["ask_date"], reply_markup=get_cancel_keyboard())
    await state.set_state(UserStates.booking_date)


@router.message(UserStates.booking_date)
async def booking_date(message: types.Message, state: FSMContext):
    """Process date."""
    if message.text == BUTTONS["cancel"]:
        await cancel_current_action(message, state)
        return
    
    # Normalize date: strip whitespace
    date_text = message.text.strip()
    
    # Validate date format DD.MM.YYYY
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date_text):
        await message.answer(MESSAGES["invalid_date_format"])
        return
    
    await state.update_data(date=date_text)
    await message.answer(MESSAGES["ask_time"], reply_markup=get_cancel_keyboard())
    await state.set_state(UserStates.booking_time)


@router.message(UserStates.booking_time)
async def booking_time(message: types.Message, state: FSMContext):
    """Process time and check slot availability."""
    if message.text == BUTTONS["cancel"]:
        await cancel_current_action(message, state)
        return
    
    # Normalize time: strip whitespace
    time_text = message.text.strip()
    
    # Validate time format HH:MM
    if not re.match(r"^\d{2}:\d{2}$", time_text):
        await message.answer(MESSAGES["invalid_time_format"])
        return
    
    # Check slot availability
    data = await state.get_data()
    subject = data["subject"]
    date = data["date"]
    
    if not is_slot_available(subject, date, time_text):
        # Slot is busy - return to date input
        await message.answer(MESSAGES["slot_busy"])
        await message.answer(MESSAGES["ask_date"], reply_markup=get_cancel_keyboard())
        await state.set_state(UserStates.booking_date)
        return
    
    await state.update_data(time=time_text)
    await message.answer(MESSAGES["ask_comment"], reply_markup=get_skip_cancel_keyboard())
    await state.set_state(UserStates.booking_comment)


@router.message(UserStates.booking_comment)
async def booking_comment(message: types.Message, state: FSMContext):
    """Process comment and show confirmation."""
    if message.text == BUTTONS["cancel"]:
        await cancel_current_action(message, state)
        return
    
    data = await state.get_data()
    
    # Handle skip
    comment = None if message.text == BUTTONS["skip"] else message.text
    
    # Save comment to state
    await state.update_data(comment=comment)
    
    # Show confirmation screen
    comment_display = comment if comment else "(нет)"
    confirmation_text = MESSAGES["booking_confirm"].format(
        data["subject"],
        data["date"],
        data["time"],
        comment_display
    )
    
    await message.answer(confirmation_text, reply_markup=get_booking_confirmation_keyboard())
    await state.set_state(UserStates.booking_confirm)


@router.callback_query(F.data == "confirm_booking", UserStates.booking_confirm)
async def confirm_booking(callback: types.CallbackQuery, state: FSMContext):
    """Confirm booking and save to database."""
    data = await state.get_data()
    
    # Check slot availability one more time before saving
    if not is_slot_available(data["subject"], data["date"], data["time"]):
        # Slot became busy - show error and return to date input
        await callback.message.edit_text(MESSAGES["slot_busy"])
        await callback.message.answer(MESSAGES["ask_date"], reply_markup=get_cancel_keyboard())
        await state.set_state(UserStates.booking_date)
        return
    
    # Save lesson to database
    create_lesson(
        student_id=callback.from_user.id,
        subject=data["subject"],
        date=data["date"],
        time=data["time"],
        comment=data["comment"]
    )
    
    comment_display = data["comment"] if data["comment"] else "(нет)"
    success_text = MESSAGES["lesson_created"].format(
        data["subject"],
        data["date"],
        data["time"],
        comment_display
    )
    
    await callback.message.edit_text(success_text)
    await callback.message.answer(MESSAGES["main_menu_student"], reply_markup=get_student_menu_keyboard())
    await state.clear()


@router.callback_query(F.data == "change_booking", UserStates.booking_confirm)
async def change_booking(callback: types.CallbackQuery, state: FSMContext):
    """Return to subject input to change booking data."""
    await callback.message.edit_text("✏️ Редактирование запроса...")
    await state.clear()
    await callback.message.answer(MESSAGES["ask_subject"], reply_markup=get_cancel_keyboard())
    await state.set_state(UserStates.booking_subject)


@router.callback_query(F.data == "cancel_booking", UserStates.booking_confirm)
async def cancel_booking(callback: types.CallbackQuery, state: FSMContext):
    """Cancel booking without saving."""
    await state.clear()
    await callback.message.edit_text(MESSAGES["booking_cancelled"])
    await callback.message.answer(MESSAGES["main_menu_student"], reply_markup=get_student_menu_keyboard())


# ==================== STUDENT: VIEW LESSONS ====================

@router.message(F.text == BUTTONS["my_lessons"])
async def view_my_lessons(message: types.Message):
    """Show student's lessons."""
    if not user_exists(message.from_user.id):
        await message.answer(MESSAGES["error"])
        return
    
    if get_user_role(message.from_user.id) != "student":
        await message.answer("❌ Только студенты могут просмотреть свои уроки")
        return
    
    lessons = get_student_lessons(message.from_user.id)
    
    if not lessons:
        await message.answer(MESSAGES["no_lessons"])
        return
    
    # Format lessons list
    lessons_text = ""
    for lesson in lessons:
        status_name = STATUS_NAMES.get(lesson[5], lesson[5])
        lessons_text += f"🔹 {lesson[1]} ({lesson[2]} {lesson[3]})\nСтатус: {status_name}\n\n"
    
    await message.answer(MESSAGES["lessons_list"].format(lessons_text))
    
    # Show inline keyboard for lesson selection
    keyboard = get_lessons_inline_keyboard(lessons, "view_lesson")
    await message.answer(MESSAGES["choose_lesson"], reply_markup=keyboard)


@router.callback_query(F.data.startswith("view_lesson_"))
async def view_lesson_details(callback: types.CallbackQuery):
    """Show lesson details."""
    lesson_id = int(callback.data.split("_")[2])
    lesson = get_lesson_by_id(lesson_id)
    
    if not lesson:
        await callback.answer("❌ Урок не найден")
        return
    
    status_name = STATUS_NAMES.get(lesson[6], lesson[6])
    lesson_text = MESSAGES["lesson_info"].format(
        lesson[0], lesson[1], lesson[2], lesson[3], lesson[4],
        lesson[5] if lesson[5] else "(нет)", status_name
    )
    
    await callback.message.edit_text(
        lesson_text,
        reply_markup=get_lesson_actions_keyboard(lesson_id)
    )


@router.callback_query(F.data.startswith("cancel_student_"))
async def cancel_student_lesson(callback: types.CallbackQuery):
    """Cancel student's lesson by changing status to cancelled."""
    lesson_id = int(callback.data.split("_")[2])
    cancel_lesson(lesson_id)
    
    await callback.answer(MESSAGES["lesson_cancelled_status"])
    await callback.message.edit_text("✅ Запись отменена")


# ==================== INFO BUTTON ====================

@router.message(F.text == BUTTONS["info"])
async def info_button(message: types.Message):
    """Handle info button."""
    await message.answer(MESSAGES["info"])


# ==================== TUTOR: VIEW REQUESTS ====================

@router.message(F.text == BUTTONS["view_requests"])
async def view_lesson_requests(message: types.Message):
    """Show all lesson requests."""
    if not user_exists(message.from_user.id):
        await message.answer(MESSAGES["error"])
        return
    
    if get_user_role(message.from_user.id) != "tutor":
        await message.answer("❌ Только преподаватели могут просмотреть запросы")
        return
    
    requests = get_all_lesson_requests()
    
    if not requests:
        await message.answer(MESSAGES["no_lessons"])
        return
    
    # Format requests list
    requests_text = ""
    for req in requests:
        status_name = STATUS_NAMES.get(req[6], req[6])
        requests_text += f"🔹 {req[1]} - {req[2]} ({req[3]} {req[4]})\nСтатус: {status_name}\n\n"
    
    await message.answer(MESSAGES["lessons_requests"].format(requests_text))
    
    # Show inline keyboard for request selection
    keyboard = get_lessons_inline_keyboard(requests, "request")
    await message.answer(MESSAGES["choose_lesson"], reply_markup=keyboard)


@router.callback_query(F.data.startswith("request_"))
async def view_request_details(callback: types.CallbackQuery):
    """Show request details."""
    lesson_id = int(callback.data.split("_")[1])
    lesson = get_lesson_by_id(lesson_id)
    
    if not lesson:
        await callback.answer("❌ Запрос не найден")
        return
    
    status_name = STATUS_NAMES.get(lesson[6], lesson[6])
    lesson_text = MESSAGES["lesson_info"].format(
        lesson[0], lesson[1], lesson[2], lesson[3], lesson[4],
        lesson[5] if lesson[5] else "(нет)", status_name
    )
    
    await callback.message.edit_text(
        lesson_text,
        reply_markup=get_tutor_lesson_actions_keyboard(lesson_id)
    )


@router.callback_query(F.data.startswith("status_"))
async def change_lesson_status(callback: types.CallbackQuery):
    """Change lesson status."""
    parts = callback.data.split("_")
    lesson_id = int(parts[1])
    status = parts[2]
    
    update_lesson_status(lesson_id, status)
    status_name = STATUS_NAMES.get(status, status)
    
    await callback.answer(MESSAGES["status_changed"].format(status_name))
    await callback.message.edit_text(f"✅ Статус изменен на: {status_name}")


# ==================== BACK TO MENU ====================

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    """Go back to menu."""
    if not user_exists(callback.from_user.id):
        await callback.answer(MESSAGES["error"])
        return
    
    role = get_user_role(callback.from_user.id)
    if role == "tutor":
        await callback.message.edit_text(MESSAGES["main_menu_tutor"], reply_markup=get_tutor_menu_keyboard())
    else:
        await callback.message.edit_text(MESSAGES["main_menu_student"], reply_markup=get_student_menu_keyboard())
