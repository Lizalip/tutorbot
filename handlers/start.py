from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import MESSAGES, BUTTONS
from models.user import UserRole
from services.user_service import UserService
from states.user_states import UserStates
from handlers.common import get_role_selection_keyboard, get_main_menu_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command."""
    user = UserService.get_user(message.from_user.id)
    
    if user:
        # User already registered, show main menu
        await message.answer(
            MESSAGES["main_menu"],
            reply_markup=get_main_menu_keyboard(user.role.value)
        )
    else:
        # New user, show role selection
        await message.answer(
            MESSAGES["welcome"],
            reply_markup=get_role_selection_keyboard()
        )
        await state.set_state(UserStates.WAITING_FOR_ROLE)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    user = UserService.get_user(message.from_user.id)
    
    if user:
        if user.role == UserRole.TUTOR:
            help_text = MESSAGES["help_tutor"]
        else:
            help_text = MESSAGES["help_student"]
        
        await message.answer(help_text)
    else:
        await message.answer(MESSAGES["error"])


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Handle /menu command."""
    user = UserService.get_user(message.from_user.id)
    
    if user:
        await message.answer(
            MESSAGES["main_menu"],
            reply_markup=get_main_menu_keyboard(user.role.value)
        )
    else:
        await message.answer(MESSAGES["error"])