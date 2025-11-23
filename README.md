# Noētica LMS - Telegram Learning Management System

A full-featured Learning Management System (LMS) built for Telegram with Mini App support. Teachers can create assignments and quizzes, while students can submit work and take tests - all within Telegram.

## 🎯 Features

### For Teachers
- **Class Management**: Link Telegram groups as classes
- **Assignments**: Create, post, and manage assignments in group chats
- **Quizzes**: Create quizzes with multiple question types (multiple choice, true/false, short answer, essay)
- **Submissions**: View and track student submissions
- **Reminders**: Send assignment reminders to students
- **Export**: Export submissions as CSV files
- **Real-time Updates**: Get instant notifications about new submissions

### For Students
- **Course Enrollment**: Enroll in courses using course codes
- **Assignments**: View all assignments from enrolled courses
- **Quiz Taking**: Take quizzes with automatic scoring
- **Progress Tracking**: Monitor completion rates and grades
- **File Uploads**: Submit assignments with text and file attachments

### Technical Features
- **Telegram Mini App**: Beautiful web interface within Telegram
- **Bot Integration**: Seamless Telegram bot for notifications and commands
- **File Storage**: Secure file upload and storage system
- **Reply-based Submissions**: Students can reply to assignment messages directly
- **JSON Database**: Lightweight file-based storage with atomic writes
- **Authentication**: Telegram WebApp initData validation

## 🏗️ Architecture

```
┌─────────────────┐
│  Telegram Bot   │ ← Commands, Messages, Notifications
└────────┬────────┘
         │
┌────────▼────────┐
│   FastAPI       │ ← REST API Server
│   Server        │
└────────┬────────┘
         │
┌────────▼────────┐
│   Mini App      │ ← Web Interface (HTML/JS)
│  (Frontend)     │
└────────┬────────┘
         │
┌────────▼────────┐
│   Storage       │ ← JSON File Database
│   (data.json)   │
└─────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- A web server with HTTPS (for hosting the Mini App)

### Step 1: Clone and Setup

```bash
git clone <your-repo>
cd Miniapp
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

Create a `.env` file:

```env
# Telegram Bot Token from @BotFather
NOETICA_BOT_TOKEN=your_bot_token_here

# URL where your mini app is hosted (must be HTTPS)
WEBAPP_URL=https://your-domain.com/miniapp

# Development mode (skip auth validation for testing)
DEV_SKIP_INITDATA_VALIDATION=false
```

### Step 4: Configure Bot Settings

1. Go to [@BotFather](https://t.me/BotFather)
2. Send `/mybots` → Select your bot
3. **Bot Settings** → **Menu Button** → Configure Web App URL
4. **Group Privacy** → Disable (allows bot to see all messages for reply capture)

## 🚀 Running the Application

### Start the API Server

```bash
cd server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://localhost:8000`

### Start the Telegram Bot

In a separate terminal:

```bash
cd bot
python bot.py
```

The bot will start polling for Telegram updates.

## 📱 Usage Guide

### For Teachers

#### 1. Link a Class
1. Create a Telegram group for your class
2. Add the bot to the group
3. Run `/init_class` in the group
4. The bot will link the group and generate a course code

#### 2. Open Dashboard
1. Send `/dashboard` to the bot in a private message
2. Click "Open LMS Dashboard" to launch the Mini App
3. You'll see all your classes and can create assignments

#### 3. Create Assignment
1. In the Mini App dashboard, click "New Assignment"
2. Fill in the title, instructions, and due date
3. Click "Create & Post"
4. The assignment will be posted and pinned in the group

#### 4. Create Quiz
1. Open the Mini App dashboard
2. Navigate to the Quizzes section
3. Click "Create Quiz"
4. Add questions (multiple choice, true/false, short answer, or essay)
5. Publish the quiz when ready

#### 5. View Submissions
1. Click on any assignment in your dashboard
2. View all student submissions
3. Export to CSV if needed
4. Send reminders to students

### For Students

#### 1. Enroll in a Course
1. Send `/dashboard` to the bot
2. Click "Open LMS Dashboard"
3. Click "Enroll in Course"
4. Enter the course code provided by your teacher

#### 2. View Assignments
1. Open the Mini App dashboard
2. Browse all assignments from your courses
3. Filter by course or search by keyword
4. Click an assignment to view details

#### 3. Submit Assignment
There are two ways to submit:

**Method A: Reply in Group**
1. Find the assignment message in the Telegram group
2. Reply to that message with your file/text
3. Bot will automatically capture your submission

**Method B: Use Mini App**
1. Open assignment in the Mini App
2. Fill in the answer text
3. Attach files if needed
4. Click "Submit"

#### 4. Take Quiz
1. Open the Mini App dashboard
2. Navigate to Quizzes
3. Click on a quiz to start
4. Answer all questions within the time limit
5. Submit to see your score

## 🔧 API Endpoints

### Teacher Endpoints
- `POST /api/classes/link` - Link a class
- `POST /api/assignments` - Create assignment
- `GET /api/assignments` - List assignments
- `PATCH /api/assignments/{id}` - Update assignment
- `GET /api/assignments/{id}/submissions` - View submissions
- `POST /api/assignments/{id}/remind` - Send reminder
- `POST /api/assignments/{id}/export_csv` - Export to CSV

### Student Endpoints
- `GET /api/student/courses` - List enrolled courses
- `POST /api/student/enroll` - Enroll in course
- `GET /api/student/assignments` - List assignments
- `GET /api/student/assignments/{id}` - Get assignment details
- `POST /api/student/assignments/{id}/submit` - Submit assignment

### Quiz Endpoints
- `POST /api/quiz/teacher/quizzes` - Create quiz
- `GET /api/quiz/teacher/quizzes` - List teacher's quizzes
- `POST /api/quiz/teacher/questions` - Add question
- `GET /api/quiz/student/quizzes` - List student's available quizzes
- `POST /api/quiz/student/attempts` - Start quiz attempt
- `POST /api/quiz/student/attempts/{id}/answer` - Answer question
- `POST /api/quiz/student/attempts/{id}/complete` - Complete quiz

## 📁 Project Structure

```
Miniapp/
├── bot/                        # Telegram bot
│   └── bot.py                  # Bot logic and command handlers
├── server/                     # FastAPI backend
│   ├── app.py                  # Main API server
│   ├── student_api.py          # Student endpoints
│   ├── quiz_api.py             # Quiz endpoints
│   └── telegram_api.py         # Telegram API helpers
├── storage/                    # Data persistence
│   ├── storage.py              # Core storage logic
│   └── quiz.py                 # Quiz storage logic
├── frontend/                   # Legacy frontend files
│   ├── teacher.html            # Teacher dashboard
│   └── student.html            # Student dashboard
├── miniapp/                    # Mini App web interface
│   └── index.html              # Main Mini App entry point
├── data/                       # Data directory
│   ├── data.json               # Database file
│   └── files/                  # Uploaded files
├── index.html                  # Simple teacher interface
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
└── README.md                   # This file
```

## 🗄️ Database Schema

The system uses a JSON file (`data/data.json`) with the following structure:

```json
{
  "meta": {
    "version": 1,
    "last_updated": "ISO timestamp"
  },
  "teachers": {
    "tg_user_id": {
      "tg_user_id": 123456,
      "name": "Teacher Name",
      "created_at": "ISO timestamp"
    }
  },
  "students": {
    "tg_user_id": {
      "tg_user_id": 789012,
      "name": "Student Name",
      "created_at": "ISO timestamp"
    }
  },
  "classes": {
    "group_chat_id": {
      "class_id": "group_chat_id",
      "title": "Class Title",
      "teacher_tg_id": 123456,
      "course_code": "ABC123XY",
      "created_at": "ISO timestamp"
    }
  },
  "assignments": {
    "assignment_id": {
      "assignment_id": "A1234567890",
      "class_id": "group_chat_id",
      "title": "Assignment Title",
      "instructions_md": "Instructions in markdown",
      "due_at": "ISO timestamp",
      "posted_message_id": 123,
      "status": "open",
      "created_at": "ISO timestamp"
    }
  },
  "submissions": {
    "submission_id": {
      "submission_id": "S1234567890",
      "assignment_id": "A1234567890",
      "student_tg_id": 789012,
      "student_name": "Student Name",
      "text": "Submission text",
      "file": {
        "file_id": "uuid",
        "filename": "file.pdf",
        "mime": "application/pdf",
        "size": 12345,
        "local_path": "/path/to/file"
      },
      "ts": "ISO timestamp",
      "late": false
    }
  },
  "enrollments": {
    "enrollment_id": {
      "enrollment_id": "E123456_-1001234567890",
      "student_tg_id": 789012,
      "class_id": "group_chat_id",
      "enrolled_at": "ISO timestamp"
    }
  },
  "quizzes": { /* quiz data */ },
  "questions": { /* question data */ },
  "quiz_attempts": { /* attempt data */ },
  "events": [ /* audit log */ ]
}
```

## 🛠️ Development

### Running in Development Mode

For local development without HTTPS:

```env
DEV_SKIP_INITDATA_VALIDATION=true
```

Then test with custom user ID header:

```bash
curl -H "x-dev-user-id: 123456" http://localhost:8000/api/health
```

### File Upload Testing

```bash
curl -X POST http://localhost:8000/api/student/assignments/A123/submit \
  -H "x-dev-user-id: 789012" \
  -F "text=My answer" \
  -F "file=@test.pdf"
```

## 🔐 Security Considerations

1. **Telegram WebApp Validation**: Implement proper HMAC validation in production
2. **File Upload**: Validate file types and sizes
3. **HTTPS**: Always use HTTPS for the Mini App URL
4. **Bot Token**: Keep your bot token secret
5. **Privacy Mode**: Disable bot privacy mode only for groups where reply capture is needed

## 🐛 Troubleshooting

### Bot not responding
- Check if bot token is correct in `.env`
- Verify bot is running with `python bot.py`
- Check bot privacy mode in BotFather

### Mini App not loading
- Ensure HTTPS is enabled
- Verify `WEBAPP_URL` in `.env` is correct
- Check if server is running and accessible

### Submissions not captured
- Ensure bot privacy mode is disabled
- Check if assignment message was posted by the bot
- Verify student replied to the correct message

### File upload fails
- Check `data/files/` directory exists and is writable
- Verify file size is within limits
- Check disk space

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📧 Support

[Add support information here]

## 🎓 Credits

Built with:
- [Python-Telegram-Bot](https://python-telegram-bot.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Telegram Mini Apps](https://core.telegram.org/bots/webapps)

---

Made with ❤️ for education

