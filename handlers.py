"""
Command and message handlers.
"""
from datetime import datetime
import re

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import MESSAGES, BUTTONS, STATUS_NAMES
from database import (
    user_exists,
    create_user,
    get_user_role,
    get_user_name,
    create_lesson,
    get_student_lessons,
    get_tutor_lesson_requests,
    get_lesson_by_id,
    update_lesson_status,
    cancel_lesson,
    is_slot_available,
    normalize_subjects_from_text,
    save_tutor_subjects,
    replace_tutor_subjects,
    get_tutor_subjects,
    get_all_unique_subjects,
    get_tutors_by_subject,
    get_available_time_slots,
)
from keyboards import (
    get_role_keyboard,
    get_student_menu_keyboard,
    get_tutor_menu_keyboard,
    get_cancel_keyboard,
    get_skip_cancel_keyboard,
    get_lessons_inline_keyboard,
    get_lesson_actions_keyboard,
    get_tutor_lesson_actions_keyboard,
    get_booking_confirmation_keyboard,
    get_subjects_inline_keyboard,
    get_tutors_inline_keyboard,
    get_time_slots_inline_keyboard,
)

router = Router()


# ==================== FSM STATES ====================

class UserStates(StatesGroup):
    """States for user conversation flow."""
    waiting_for_role = State()
    waiting_for_name = State()
    waiting_for_tutor_subjects = State()

    editing_tutor_subjects = State()

    booking_subject = State()
    booking_tutor = State()
    booking_date = State()
    booking_time = State()
    booking_comment = State()
    booking_confirm = State()


# ==================== HELPER FUNCTIONS ====================

async def show_main_menu(message: types.Message, telegram_id: int) -> None:
    """Show the correct main menu for the user."""
    role = get_user_role(telegram_id)

    if role == "tutor":
        await message.answer(MESSAGES["main_menu_tutor"], reply_markup=get_tutor_menu_keyboard())
    else:
        await message.answer(MESSAGES["main_menu_student"], reply_markup=get_student_menu_keyboard())


async def cancel_current_action(message: types.Message, state: FSMContext) -> None:
    """
    Cancel the current unfinished FSM scenario.
    Clear state and return user to the appropriate menu.
    """
    await state.clear()

    if not user_exists(message.from_user.id):
        await message.answer(MESSAGES["welcome"], reply_markup=get_role_keyboard())
        await state.set_state(UserStates.waiting_for_role)
        return

    await show_main_menu(message, message.from_user.id)


async def start_booking_flow(message: types.Message, state: FSMContext) -> None:
    """Start booking flow from subject selection."""
    subjects = get_all_unique_subjects()

    if not subjects:
        await message.answer(MESSAGES["no_subjects_available"])
        await show_main_menu(message, message.from_user.id)
        return

    await state.clear()
    await state.update_data(subjects=subjects)

    await message.answer(
        MESSAGES["choose_subject"],
        reply_markup=get_subjects_inline_keyboard(subjects),
    )
    await state.set_state(UserStates.booking_subject)


def format_subjects(subjects: list[str]) -> str:
    """Format subjects list for user-facing messages."""
    return ", ".join(subjects) if subjects else "—"


def validate_future_date(date_text: str) -> tuple[bool, str | None]:
    """
    Validate date:
    - format DD.MM.YYYY
    - real calendar date
    - strictly later than today
    """
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date_text):
        return False, MESSAGES["invalid_date_format"]

    try:
        lesson_date = datetime.strptime(date_text, "%d.%m.%Y").date()
    except ValueError:
        return False, MESSAGES["invalid_date_value"]

    today = datetime.now().date()

    if lesson_date <= today:
        return False, MESSAGES["past_or_today_date_error"]

    return True, None


# ==================== START & HELP & INFO ====================

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Handle /start command."""
    await state.clear()

    if user_exists(message.from_user.id):
        await show_main_menu(message, message.from_user.id)
        return

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
async def cmd_menu(message: types.Message, state: FSMContext):
    """Handle /menu command."""
    await state.clear()

    if not user_exists(message.from_user.id):
        await message.answer(MESSAGES["error"])
        return

    await show_main_menu(message, message.from_user.id)


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Handle /cancel command - cancel unfinished scenario."""
    current_state = await state.get_state()

    if current_state:
        await message.answer(MESSAGES["current_action_cancelled"])
        await cancel_current_action(message, state)
        return

    await message.answer(MESSAGES["no_active_action"])

    if user_exists(message.from_user.id):
        await show_main_menu(message, message.from_user.id)


# ==================== ROLE SELECTION & NAME ====================

@router.message(UserStates.waiting_for_role, F.text == BUTTONS["tutor"])
async def choose_tutor(message: types.Message, state: FSMContext):
    """User chooses tutor role."""
    await state.update_data(role="tutor")
    await message.answer(MESSAGES["ask_name"], reply_markup=get_cancel_keyboard())
    await state.set_state(UserStates.waiting_for_name)


@router.message(UserStates.waiting_for_role, F.text == BUTTONS["student"])
async def choose_student(message: types.Message, state: FSMContext):
    """User chooses student role."""
    await state.update_data(role="student")
    await message.answer(MESSAGES["ask_name"], reply_markup=get_cancel_keyboard())
    await state.set_state(UserStates.waiting_for_name)


@router.message(UserStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Process user name."""
    if message.text == BUTTONS["cancel"]:
        await cancel_current_action(message, state)
        return

    name = message.text.strip()

    if not name or len(name) < 2:
        await message.answer(MESSAGES["invalid_input"])
        return

    data = await state.get_data()
    role = data["role"]

    create_user(message.from_user.id, name, role)

    role_display = "Преподаватель" if role == "tutor" else "Ученик"
    await message.answer(MESSAGES["role_selected"].format(role_display))

    if role == "tutor":
        await message.answer(MESSAGES["ask_tutor_subjects"], reply_markup=get_cancel_keyboard())
        await state.set_state(UserStates.waiting_for_tutor_subjects)
        return

    await message.answer(MESSAGES["main_menu_student"], reply_markup=get_student_menu_keyboard())
    await state.clear()


@router.message(UserStates.waiting_for_tutor_subjects)
async def process_tutor_subjects_after_registration(message: types.Message, state: FSMContext):
    """Save tutor subjects after tutor registration."""
    if message.text == BUTTONS["cancel"]:
        await cancel_current_action(message, state)
        return

    subjects = normalize_subjects_from_text(message.text)

    if not subjects:
        await message.answer(MESSAGES["empty_subjects_error"])
        return

    save_tutor_subjects(message.from_user.id, subjects)

    await message.answer(MESSAGES["tutor_subjects_saved"].format(format_subjects(subjects)))
    await message.answer(MESSAGES["main_menu_tutor"], reply_markup=get_tutor_menu_keyboard())

    await state.clear()


# ==================== TUTOR: EDIT SUBJECTS ====================

@router.message(F.text == BUTTONS["edit_subjects"])
async def edit_tutor_subjects_start(message: types.Message, state: FSMContext):
    """Start editing tutor subjects."""
    if not user_exists(message.from_user.id):
        await message.answer(MESSAGES["error"])
        return

    if get_user_role(message.from_user.id) != "tutor":
        await message.answer("❌ Только преподаватели могут изменять список предметов.")
        return

    subjects = get_tutor_subjects(message.from_user.id)
    subjects_text = format_subjects(subjects)

    await message.answer(
        MESSAGES["edit_subjects_prompt"].format(subjects_text),
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(UserStates.editing_tutor_subjects)


@router.message(UserStates.editing_tutor_subjects)
async def process_tutor_subjects_edit(message: types.Message, state: FSMContext):
    """Replace tutor subjects."""
    if message.text == BUTTONS["cancel"]:
        await cancel_current_action(message, state)
        return

    subjects = normalize_subjects_from_text(message.text)

    if not subjects:
        await message.answer(MESSAGES["empty_subjects_error"])
        return

    replace_tutor_subjects(message.from_user.id, subjects)

    await message.answer(MESSAGES["tutor_subjects_updated"].format(format_subjects(subjects)))
    await message.answer(MESSAGES["main_menu_tutor"], reply_markup=get_tutor_menu_keyboard())

    await state.clear()


# ==================== STUDENT: BOOK LESSON ====================

@router.message(F.text == BUTTONS["book_lesson"])
async def book_lesson_start(message: types.Message, state: FSMContext):
    """Start lesson booking."""
    if not user_exists(message.from_user.id):
        await message.answer(MESSAGES["error"])
        return

    if get_user_role(message.from_user.id) != "student":
        await message.answer("❌ Только ученики могут записаться на урок.")
        return

    await start_booking_flow(message, state)


@router.callback_query(UserStates.booking_subject, F.data.startswith("subject_"))
async def choose_subject_callback(callback: types.CallbackQuery, state: FSMContext):
    """Process subject selection from inline keyboard."""
    data = await state.get_data()
    subjects = data.get("subjects", [])

    try:
        subject_index = int(callback.data.split("_")[1])
        subject = subjects[subject_index]
    except (IndexError, ValueError):
        await callback.answer(MESSAGES["error"])
        return

    tutors = get_tutors_by_subject(subject)

    if not tutors:
        await callback.message.edit_text(MESSAGES["no_tutors_for_subject"])
        await start_booking_flow(callback.message, state)
        return

    await state.update_data(subject=subject, tutors=tutors)

    await callback.message.edit_text(
        f"📚 Вы выбрали предмет: {subject}\n\n{MESSAGES['choose_tutor']}",
        reply_markup=get_tutors_inline_keyboard(tutors),
    )
    await state.set_state(UserStates.booking_tutor)


@router.callback_query(UserStates.booking_tutor, F.data.startswith("tutor_"))
async def choose_tutor_callback(callback: types.CallbackQuery, state: FSMContext):
    """Process tutor selection from inline keyboard."""
    tutor_id_text = callback.data.replace("tutor_", "")

    try:
        tutor_id = int(tutor_id_text)
    except ValueError:
        await callback.answer(MESSAGES["error"])
        return

    tutor_name = get_user_name(tutor_id)

    if not tutor_name:
        await callback.answer(MESSAGES["error"])
        return

    await state.update_data(tutor_id=tutor_id, tutor_name=tutor_name)

    await callback.message.edit_text(f"👨‍🏫 Вы выбрали преподавателя: {tutor_name}")
    await callback.message.answer(MESSAGES["ask_date_future"], reply_markup=get_cancel_keyboard())

    await state.set_state(UserStates.booking_date)


@router.message(UserStates.booking_date)
async def booking_date(message: types.Message, state: FSMContext):
    """Process date and show available time slots."""
    if message.text == BUTTONS["cancel"]:
        await cancel_current_action(message, state)
        return

    date_text = message.text.strip()

    is_valid, error_message = validate_future_date(date_text)

    if not is_valid:
        await message.answer(error_message)
        return

    data = await state.get_data()
    tutor_id = data["tutor_id"]

    free_slots = get_available_time_slots(tutor_id, date_text)

    if not free_slots:
        await message.answer(MESSAGES["no_free_slots"])
        await message.answer(MESSAGES["ask_date_future"], reply_markup=get_cancel_keyboard())
        await state.set_state(UserStates.booking_date)
        return

    await state.update_data(date=date_text, free_slots=free_slots)

    await message.answer(
        MESSAGES["choose_time_slot"],
        reply_markup=get_time_slots_inline_keyboard(free_slots),
    )
    await state.set_state(UserStates.booking_time)


@router.callback_query(UserStates.booking_time, F.data.startswith("time_"))
async def choose_time_callback(callback: types.CallbackQuery, state: FSMContext):
    """Process time slot selection from inline keyboard."""
    time_text = callback.data.replace("time_", "").replace("_", ":")

    data = await state.get_data()
    tutor_id = data["tutor_id"]
    date = data["date"]

    if not is_slot_available(tutor_id, date, time_text):
        await callback.message.edit_text(MESSAGES["slot_busy"])
        await callback.message.answer(MESSAGES["ask_date_future"], reply_markup=get_cancel_keyboard())
        await state.set_state(UserStates.booking_date)
        return

    await state.update_data(time=time_text)

    await callback.message.edit_text(f"🕐 Вы выбрали время: {time_text}")
    await callback.message.answer(MESSAGES["ask_comment"], reply_markup=get_skip_cancel_keyboard())

    await state.set_state(UserStates.booking_comment)


@router.message(UserStates.booking_comment)
async def booking_comment(message: types.Message, state: FSMContext):
    """Process comment and show confirmation."""
    if message.text == BUTTONS["cancel"]:
        await cancel_current_action(message, state)
        return

    data = await state.get_data()

    comment = None if message.text == BUTTONS["skip"] else message.text.strip()
    await state.update_data(comment=comment)

    comment_display = comment if comment else "(нет)"

    confirmation_text = MESSAGES["booking_confirm"].format(
        data["subject"],
        data["tutor_name"],
        data["date"],
        data["time"],
        comment_display,
    )

    await message.answer(confirmation_text, reply_markup=get_booking_confirmation_keyboard())
    await state.set_state(UserStates.booking_confirm)


@router.callback_query(UserStates.booking_confirm, F.data == "confirm_booking")
async def confirm_booking(callback: types.CallbackQuery, state: FSMContext):
    """Confirm booking and save to database."""
    data = await state.get_data()

    if not is_slot_available(data["tutor_id"], data["date"], data["time"]):
        await callback.message.edit_text(MESSAGES["slot_busy"])
        await callback.message.answer(MESSAGES["ask_date_future"], reply_markup=get_cancel_keyboard())
        await state.set_state(UserStates.booking_date)
        return

    create_lesson(
        student_id=callback.from_user.id,
        tutor_id=data["tutor_id"],
        subject=data["subject"],
        date=data["date"],
        time=data["time"],
        comment=data.get("comment"),
    )

    comment_display = data.get("comment") if data.get("comment") else "(нет)"

    success_text = MESSAGES["lesson_created"].format(
        data["subject"],
        data["tutor_name"],
        data["date"],
        data["time"],
        comment_display,
    )

    await callback.message.edit_text(success_text)
    await callback.message.answer(MESSAGES["main_menu_student"], reply_markup=get_student_menu_keyboard())

    await state.clear()


@router.callback_query(UserStates.booking_confirm, F.data == "change_booking")
async def change_booking(callback: types.CallbackQuery, state: FSMContext):
    """Restart booking flow from subject selection."""
    await callback.message.edit_text("✏️ Редактирование заявки...")
    await start_booking_flow(callback.message, state)


@router.callback_query(UserStates.booking_confirm, F.data == "cancel_booking")
async def cancel_booking(callback: types.CallbackQuery, state: FSMContext):
    """Cancel booking without saving."""
    await state.clear()

    await callback.message.edit_text(MESSAGES["booking_cancelled"])
    await callback.message.answer(MESSAGES["main_menu_student"], reply_markup=get_student_menu_keyboard())


@router.callback_query(F.data == "cancel_flow")
async def cancel_flow_callback(callback: types.CallbackQuery, state: FSMContext):
    """Cancel current flow from inline keyboard if such button exists."""
    await state.clear()

    await callback.message.edit_text(MESSAGES["current_action_cancelled"])
    await show_main_menu(callback.message, callback.from_user.id)


# ==================== STUDENT: VIEW LESSONS ====================

@router.message(F.text == BUTTONS["my_lessons"])
async def view_my_lessons(message: types.Message):
    """Show student's lessons."""
    if not user_exists(message.from_user.id):
        await message.answer(MESSAGES["error"])
        return

    if get_user_role(message.from_user.id) != "student":
        await message.answer("❌ Только ученики могут просмотреть свои уроки.")
        return

    lessons = get_student_lessons(message.from_user.id)

    if not lessons:
        await message.answer(MESSAGES["no_lessons"])
        return

    lessons_text = ""

    for lesson in lessons:
        # lesson: id, subject, lesson_date, lesson_time, comment, status, tutor_name
        status_name = STATUS_NAMES.get(lesson[5], lesson[5])
        lessons_text += (
            f"🔹 {lesson[1]} — {lesson[6]}\n"
            f"Дата и время: {lesson[2]} {lesson[3]}\n"
            f"Статус: {status_name}\n\n"
        )

    await message.answer(MESSAGES["lessons_list"].format(lessons_text))

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

    # lesson: id, student_name, tutor_name, subject, lesson_date, lesson_time, comment, status
    status_name = STATUS_NAMES.get(lesson[7], lesson[7])

    lesson_text = MESSAGES["lesson_info"].format(
        lesson[0],
        lesson[1],
        lesson[2],
        lesson[3],
        lesson[4],
        lesson[5],
        lesson[6] if lesson[6] else "(нет)",
        status_name,
    )

    await callback.message.edit_text(
        lesson_text,
        reply_markup=get_lesson_actions_keyboard(lesson_id),
    )


@router.callback_query(F.data.startswith("cancel_student_"))
async def cancel_student_lesson(callback: types.CallbackQuery):
    """Cancel student's lesson by changing status to cancelled."""
    lesson_id = int(callback.data.split("_")[2])
    cancel_lesson(lesson_id)

    await callback.answer(MESSAGES["lesson_cancelled_status"])
    await callback.message.edit_text(MESSAGES["lesson_cancelled_status"])


# ==================== INFO BUTTON ====================

@router.message(F.text == BUTTONS["info"])
async def info_button(message: types.Message):
    """Handle info button."""
    await message.answer(MESSAGES["info"])


# ==================== TUTOR: VIEW REQUESTS ====================

@router.message(F.text == BUTTONS["view_requests"])
async def view_lesson_requests(message: types.Message):
    """Show tutor's lesson requests."""
    if not user_exists(message.from_user.id):
        await message.answer(MESSAGES["error"])
        return

    if get_user_role(message.from_user.id) != "tutor":
        await message.answer("❌ Только преподаватели могут просмотреть запросы.")
        return

    requests = get_tutor_lesson_requests(message.from_user.id)

    if not requests:
        await message.answer(MESSAGES["no_lessons"])
        return

    requests_text = ""

    for req in requests:
        # req: id, student_name, subject, lesson_date, lesson_time, comment, status, tutor_name
        status_name = STATUS_NAMES.get(req[6], req[6])
        requests_text += (
            f"🔹 {req[1]} — {req[2]}\n"
            f"Дата и время: {req[3]} {req[4]}\n"
            f"Статус: {status_name}\n\n"
        )

    await message.answer(MESSAGES["lessons_requests"].format(requests_text))

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

    # lesson: id, student_name, tutor_name, subject, lesson_date, lesson_time, comment, status
    status_name = STATUS_NAMES.get(lesson[7], lesson[7])

    lesson_text = MESSAGES["lesson_info"].format(
        lesson[0],
        lesson[1],
        lesson[2],
        lesson[3],
        lesson[4],
        lesson[5],
        lesson[6] if lesson[6] else "(нет)",
        status_name,
    )

    await callback.message.edit_text(
        lesson_text,
        reply_markup=get_tutor_lesson_actions_keyboard(lesson_id),
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
    await callback.message.edit_text(f"✅ Статус изменён на: {status_name}")


# ==================== BACK TO MENU ====================

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    """Go back to menu."""
    if not user_exists(callback.from_user.id):
        await callback.answer(MESSAGES["error"])
        return

    await callback.message.edit_text("🏠 Возврат в главное меню")
    await show_main_menu(callback.message, callback.from_user.id)