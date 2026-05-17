# 📚 Lesson Booking Bot

A simple Russian-language Telegram bot for booking tutoring lessons.

## ✨ Features

- 👥 **Two roles**: Student and Tutor
- 📝 **Lesson booking**: Students can book lessons by subject, date, and time
- 📋 **View lessons**: Students view their bookings, tutors view all requests
- 🔄 **Status management**: Tutors can mark lessons as planned, completed, or cancelled
- 🗑️ **Cancellation**: Both students and tutors can cancel lessons
- 🗄️ **SQLite database**: Simple local storage
- 🌍 **Russian interface**: All buttons and messages in Russian

## 🎯 Target Audience

- Students who want to book tutoring lessons
- Tutors who manage lesson requests
- Educational centers or individual tutors

## 📋 Requirements

- Python 3.11+
- pip (Python package manager)
- Telegram account
- Telegram Bot Token (get from @BotFather)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Lizalip/tutorbot.git
cd tutorbot
```

### 2. Create virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your bot token:

```
TELEGRAM_BOT_TOKEN=your_token_here
```

**How to get a Telegram Bot Token:**
1. Open Telegram
2. Find @BotFather
3. Send `/newbot`
4. Follow instructions
5. Copy the token to `.env`

### 5. Run the bot

```bash
python main.py
```

You should see:
```
✅ Database initialized
✅ Bot commands set
🚀 Bot started polling...
```

## 📖 Usage

### For New Users
1. Send `/start` to the bot
2. Choose your role (Student or Tutor)
3. Enter your name

### For Students
- `/book_lesson` - Book a new lesson (enter subject, date, time, optional comment)
- `/my_lessons` - View your booked lessons
- Delete your lessons from the lesson list

### For Tutors
- `/view_requests` - See all lesson requests
- Change lesson status: Planned, Completed, or Cancelled
- Delete lessons if needed

### Commands (Any Time)
- `/start` - Start the bot
- `/help` - Get help
- `/menu` - Return to main menu

## 🗄️ Database Schema

### Users Table
```
id              - Primary key
telegram_id     - Unique Telegram user ID
name            - User's name
role            - "tutor" or "student"
created_at      - Creation timestamp
```

### Lessons Table
```
id              - Primary key
student_id      - Foreign key to users.telegram_id
subject         - Lesson subject
lesson_date     - Date in DD.MM.YYYY format
lesson_time     - Time in HH:MM format
comment         - Optional comment from student
status          - "planned", "completed", or "cancelled"
created_at      - Creation timestamp
```

## 📁 Project Structure

```
lesson_booking_bot/
├── main.py              # Bot entry point
├── handlers.py          # All command handlers
├── database.py          # Database setup and queries
├── keyboards.py         # Button layouts
├── config.py            # Configuration and messages
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🏗️ Architecture

Simple, single-file architecture:
- **main.py**: Bot initialization and polling
- **handlers.py**: All Telegram message and command handlers using FSM
- **database.py**: SQLite database operations
- **keyboards.py**: Button layouts and keyboard creation
- **config.py**: Configuration, messages, and labels in Russian

No complex layers or dependencies beyond aiogram and sqlite3.

## 🛡️ Security

- Bot token stored in `.env` (not in code)
- SQLite database is local (no cloud storage)
- No sensitive data transmission
- Role-based access control (students see only their lessons)

## 📊 Functional Requirements

- ✅ User registration with role selection
- ✅ Lesson booking by students
- ✅ View personal lessons (students)
- ✅ View all lesson requests (tutors)
- ✅ Change lesson status (tutors)
- ✅ Cancel lessons
- ✅ Date and time validation

## ⚡ Non-Functional Requirements

- ✅ Response time < 2 seconds
- ✅ Support for 100+ concurrent users
- ✅ Simple local deployment
- ✅ Readable and maintainable code
- ✅ Russian-language interface

## 🔮 Future Enhancements

- Email notifications for lesson confirmations
- Rating and feedback system
- Payment integration
- Calendar view of lessons
- Automatic reminders before lessons
- Admin statistics panel

## 🧪 Testing

To test the bot locally:

1. Start the bot: `python main.py`
2. Open Telegram and find your bot
3. Send `/start` and complete the onboarding
4. Try booking a lesson (as student) or viewing requests (as tutor)
5. Test all features

## 📝 Code Comments

The code is well-commented in English, making it suitable for a course project. All user-facing text is in Russian.

## ⚠️ Troubleshooting

**Bot doesn't respond:**
- Check `.env` file has correct token
- Verify bot token is valid with @BotFather
- Check internet connection

**Database errors:**
- Delete `lessons.db` to reset database
- Make sure folder is writable

**Import errors:**
- Run `pip install -r requirements.txt` again
- Verify Python 3.11+

## 👨‍🎓 Academic Use

This project is designed to be a course project demonstrating:
- Async programming with aiogram
- Telegram API integration
- Database design principles
- State machine patterns in chatbots
- Clean code organization

## 📚 How to Describe This Project in a Course Paper

### Project Title
"Разработка Telegram-бота для записи на уроки репетиторов"
(Development of a Telegram Bot for Tutoring Lesson Booking)

### Problem Statement
Modern tutors and students struggle with organized lesson scheduling. Email and messaging apps create communication chaos. This project solves the problem by providing a structured, intuitive interface for booking and managing lessons.

### Target Audience
- Students seeking tutoring services
- Independent tutors managing multiple students
- Educational centers

### Functional Requirements (in paper)
1. User registration with role selection (Student/Tutor)
2. Lesson booking with subject, date, time, optional comment
3. View personal lessons (students) or all requests (tutors)
4. Change lesson status (planned/completed/cancelled)
5. Cancel lessons

### Non-Functional Requirements (in paper)
- Fast response time (< 2 seconds)
- Support 100+ concurrent users
- Simple deployment (local SQLite)
- Intuitive Russian interface
- Reliable data storage

### Technical Stack (in paper)
- Python 3.11+
- aiogram 3.x (Telegram bot framework)
- SQLite (database)
- python-dotenv (configuration)

### Architecture (in paper)
- Single-file handler architecture (suitable for MVP)
- Finite State Machine for user interactions
- Direct database queries (no ORM, simple SQLite)
- Modular organization (config, database, handlers, keyboards)

### Database Design (in paper)
- **Users**: Stores user profiles with roles
- **Lessons**: Stores booking requests with status tracking

### Implementation Highlights (in paper)
- Async/await patterns with aiogram
- Input validation for dates and times
- Role-based access control
- Status management workflow
- User-friendly error messages

### Testing (in paper)
- Functional testing: all user scenarios
- Edge cases: invalid dates, permission checks
- Manual testing in Telegram

### Results (in paper)
- Fully functional lesson booking bot
- Working database with proper relationships
- Clean, maintainable code suitable for production
- Deployed and tested successfully

### Possible Improvements (in paper)
- Add email notifications
- Implement rating system
- Integrate payment processing
- Add calendar view
- Automatic lesson reminders
- Admin statistics panel

### Conclusion
This project demonstrates practical application of Telegram bot development, database design, and state machine patterns. The simple architecture makes it ideal for course work while being realistic enough for actual use.

---

## 📄 License

MIT License - Free to use for educational purposes.

## 👨‍💻 Author

Course project for learning bot development.

## 📞 Support

Found a bug? Create an issue or ask for help.

---

**Ready to book lessons? 🚀**
