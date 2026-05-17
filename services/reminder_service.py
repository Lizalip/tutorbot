from datetime import datetime, timedelta
from models.lesson import LessonStatus
from services.lesson_service import LessonService


class ReminderService:
    """Service for handling reminders about upcoming lessons."""

    @staticmethod
    def get_lessons_needing_reminder(minutes_until: int = 60):
        """
        Get lessons that need reminders (happening in the next N minutes).
        
        Args:
            minutes_until: Number of minutes to look ahead for reminders
        
        Returns:
            List of lessons needing reminders
        """
        return LessonService.get_upcoming_lessons(minutes_until)

    @staticmethod
    def format_lesson_reminder(lesson) -> str:
        """Format a lesson reminder message in Russian."""
        date_str = lesson.date.strftime("%d.%m.%Y")
        time_str = lesson.date.strftime("%H:%M")
        
        message = f"""⏰ <b>Напоминание об уроке!</b>

📚 Предмет: {lesson.subject}
📅 Дата: {date_str}
🕐 Время: {time_str}
⏱ Продолжительность: {lesson.duration_minutes} мин"""
        
        if lesson.comment:
            message += f"\n📝 Примечание: {lesson.comment}"
        
        return message

    @staticmethod
    def check_and_send_reminders(bot_instance):
        """
        Check for upcoming lessons and send reminders.
        This function should be called periodically (e.g., every 10 minutes).
        
        NOTE: This is a placeholder implementation. In production, you would use:
        - APScheduler for robust scheduling
        - AsyncIO tasks for async operations
        - Proper error handling and logging
        
        Args:
            bot_instance: The aiogram bot instance
        """
        # This would be implemented in the main bot loop
        # See main.py for the actual implementation
        pass