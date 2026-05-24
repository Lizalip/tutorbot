"""
Main bot entry point.
"""
import asyncio
import logging
import os
from os import getenv

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties

from database import init_db
from handlers import router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env file")


async def set_commands(bot: Bot):
    """Set bot commands."""
    commands = [
        BotCommand(command="start", description="Начало работы"),
        BotCommand(command="help", description="Справка"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="cancel", description="Отмена текущего действия"),
        BotCommand(command="info", description="Информация о занятиях"),
    ]
    await bot.set_my_commands(commands)


async def main():
    """Main bot function."""
    # Initialize database
    init_db()
    logger.info("✅ Database initialized")
    
    # Create bot instance
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    
    # Create dispatcher
    dp = Dispatcher()
    dp.include_router(router)
    
    # Set commands
    await set_commands(bot)
    logger.info("✅ Bot commands set")
    
    # Delete webhook and start polling
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("🚀 Bot started polling...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
