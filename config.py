import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env file")

# Database configuration
DATABASE_URL = "sqlite:///./tutorbot.db"

# Bot settings
BOT_COMMAND_PREFIX = "/"
DEFAULT_PARSE_MODE = "HTML"

# Text messages in Russian
MESSAGES = {
    "welcome": """👋 Добро пожаловать в TutorBot!

Я помогу вам организовать процесс обучения, управлять расписанием уроков и домашними заданиями.

Сначала выберите вашу роль:""",
    
    "role_selected": "✅ Спасибо! Вы зарегистрированы как {}",
    
    "main_menu": """📚 Главное меню

Выберите действие:""",
    
    "help_tutor": """📖 Справка для репетитора

Доступные команды:
• <b>/lessons</b> - Мои уроки
• <b>/add_lesson</b> - Добавить урок
• <b>/homework</b> - Задания студентов
• <b>/assign_homework</b> - Выдать задание
• <b>/notes</b> - Мои заметки
• <b>/add_note</b> - Добавить заметку
• <b>/menu</b> - Главное меню""",
    
    "help_student": """📖 Справка для студента

Доступные команды:
• <b>/lessons</b> - Мои уроки
• <b>/homework</b> - Мои задания
• <b>/menu</b> - Главное меню""",
    
    "error": "❌ Произошла ошибка. Попробуйте еще раз.",
    "invalid_input": "⚠️ Неверный ввод. Пожалуйста, попробуйте еще раз.",
}

# Keyboard buttons in Russian
BUTTONS = {
    "tutor": "👨‍🏫 Репетитор",
    "student": "👨‍🎓 Студент",
    "lessons": "📚 Уроки",
    "add_lesson": "➕ Добавить урок",
    "homework": "📝 Домашние задания",
    "assign_homework": "✏️ Выдать задание",
    "notes": "📄 Заметки",
    "add_note": "📝 Добавить заметку",
    "menu": "🏠 Главное меню",
    "back": "⬅️ Назад",
    "cancel": "❌ Отмена",
    "yes": "✅ Да",
    "no": "❌ Нет",
    "complete": "✅ Завершить",
    "cancel_lesson": "❌ Отменить",
    "mark_completed": "✅ Отметить выполнено",
    "view_notes": "👀 Просмотреть заметки",
}