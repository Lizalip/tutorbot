from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from config import MESSAGES, BUTTONS
from models.user import UserRole
from services.user_service import UserService
from states.user_states import UserStates
from handlers.common import get_role_selection_keyboard, get_main_menu_keyboard

router = Router()


@router.message(UserStates.WAITING_FOR_ROLE)
async def process_role_selection(message: Message, state: FSMContext):
    """Process user role selection."""
    if message.text == BUTTONS["tutor"]:
        role = UserRole.TUTOR
        role_display = "репетитор"
    elif message.text == BUTTONS["student"]:
        role = UserRole.STUDENT
        role_display = "студент"
    else:
        await message.answer(MESSAGES["invalid_input"])
        return
    
    # Save role to FSM context
    await state.update_data(role=role)
    
    # Ask for name
    await message.answer("👤 Как вас зовут?")
    await state.set_state(UserStates.WAITING_FOR_NAME)


@router.message(UserStates.WAITING_FOR_NAME)
async def process_name_input(message: Message, state: FSMContext):
    """Process user name input."""
    name = message.text.strip()
    
    if not name or len(name) < 2:
        await message.answer("⚠️ Пожалуйста, введите корректное имя")
        return
    
    # Get data from FSM context
    data = await state.get_data()
    role = data.get("role")
    
    # Create user in database
    user = UserService.create_user(
        telegram_id=message.from_user.id,
        name=name,
        role=role
    )
    
    role_display = "репетитор" if role == UserRole.TUTOR else "студент"
    
    # Confirm registration
    await message.answer(
        MESSAGES["role_selected"].format(role_display),
        reply_markup=get_main_menu_keyboard(role.value)
    )
    
    # Clear state
    await state.clear()