# Noētica LMS - Setup Guide

This guide will walk you through setting up your Telegram LMS system from scratch.

## Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.8 or higher installed
- ✅ A Telegram account
- ✅ Basic knowledge of command line
- ✅ A server with HTTPS (for production) or ngrok (for testing)

## Part 1: Creating Your Telegram Bot

### Step 1: Talk to BotFather

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` to create a new bot
3. Choose a name for your bot (e.g., "My School LMS")
4. Choose a username (must end in 'bot', e.g., "myschool_lms_bot")
5. **Save the bot token** - you'll need it later!

### Step 2: Configure Bot Settings

With BotFather, configure your bot:

1. Send `/mybots` and select your bot
2. Click **Bot Settings** → **Menu Button**
3. Enter your Mini App URL (we'll set this up later)
4. Click **Group Privacy** → **Turn Off**
   - This allows the bot to see messages in groups (needed for reply-based submissions)

### Step 3: Optional Settings

You can also:
- Set a profile picture: `/setuserpic`
- Add a description: `/setdescription`
- Set commands: `/setcommands` then paste:
  ```
  start - Start the bot
  dashboard - Open the LMS dashboard
  init_class - Link a Telegram group as a class (use in group chat)
  ```

## Part 2: Installing the Application

### Step 1: Download the Code

```bash
# Clone the repository
git clone <your-repository-url>
cd Miniapp
```

### Step 2: Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `fastapi` - Web framework for the API
- `uvicorn` - ASGI server
- `python-telegram-bot` - Telegram bot library
- `pydantic` - Data validation
- `requests` - HTTP requests
- `python-dotenv` - Environment variable management
- `python-multipart` - File upload support

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit the file
nano .env  # or use your preferred editor
```

Fill in your configuration:

```env
# Your bot token from BotFather
NOETICA_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# URL where your mini app will be accessible
WEBAPP_URL=https://your-domain.com/miniapp

# For local testing only - set to true
DEV_SKIP_INITDATA_VALIDATION=false
```

## Part 3: Setting Up Your Server

You have two options: Local Testing or Production Deployment

### Option A: Local Testing with ngrok

For development and testing:

1. **Install ngrok**
   ```bash
   # Download from https://ngrok.com/download
   # Or using package manager:
   
   # macOS
   brew install ngrok
   
   # Windows (with Chocolatey)
   choco install ngrok
   ```

2. **Start ngrok tunnel**
   ```bash
   ngrok http 8000
   ```
   
   You'll see output like:
   ```
   Forwarding    https://abc123.ngrok.io -> http://localhost:8000
   ```

3. **Update your .env file**
   ```env
   WEBAPP_URL=https://abc123.ngrok.io/miniapp
   DEV_SKIP_INITDATA_VALIDATION=true  # For testing
   ```

4. **Update BotFather**
   - Go to BotFather
   - Send `/mybots` → select your bot
   - **Bot Settings** → **Menu Button**
   - Set URL to: `https://abc123.ngrok.io/miniapp`

### Option B: Production Server

For production deployment:

1. **Choose a hosting provider**
   - AWS, Google Cloud, DigitalOcean, Heroku, etc.
   - Must support HTTPS

2. **Set up SSL/TLS**
   - Use Let's Encrypt (free) or your provider's SSL
   - Telegram requires HTTPS for Mini Apps

3. **Configure reverse proxy** (example with Nginx)
   ```nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Update .env**
   ```env
   WEBAPP_URL=https://your-domain.com/miniapp
   DEV_SKIP_INITDATA_VALIDATION=false
   ```

## Part 4: Running the Application

### Terminal 1: Start the API Server

```bash
# Navigate to the project directory
cd Miniapp

# Start the FastAPI server
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Terminal 2: Start the Telegram Bot

Open a new terminal:

```bash
# Navigate to the project directory
cd Miniapp

# Start the bot
python bot/bot.py
```

You should see:
```
Bot polling…
```

## Part 5: Testing Your Setup

### Test 1: Check API Health

Open your browser or use curl:
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"ok": true}
```

### Test 2: Test Bot Commands

1. Open Telegram
2. Search for your bot
3. Send `/start`
4. You should receive a welcome message

### Test 3: Create a Test Class

1. Create a Telegram group (or use an existing one)
2. Add your bot to the group
3. Send `/init_class` in the group
4. Bot should confirm the class is linked

### Test 4: Open Mini App

1. Send `/dashboard` to the bot in a private message
2. Click the "Open LMS Dashboard" button
3. The Mini App should load in Telegram

## Part 6: Creating Your First Assignment

### As a Teacher:

1. **Open the dashboard**
   - Send `/dashboard` to your bot
   - Click "Open LMS Dashboard"

2. **Link your class** (if not done already)
   - In the dashboard, enter your group chat ID
   - You can get this from the group info or the bot logs
   - Click "Link Class"

3. **Create an assignment**
   - Click "New Assignment"
   - Fill in:
     - Title: "Welcome Assignment"
     - Instructions: "Introduce yourself in 100 words"
     - Due date: (optional) Set a deadline
   - Click "Create & Post"

4. **Check the group**
   - The assignment should appear in your Telegram group
   - It will be pinned automatically (if bot has permissions)

### As a Student:

1. **Enroll in the course**
   - Send `/dashboard` to the bot
   - Click "Open LMS Dashboard"
   - Click "Enroll in Course"
   - Enter the course code (ask your teacher)

2. **View assignments**
   - Browse all assignments from the dashboard
   - Click on an assignment to see details

3. **Submit an assignment**
   
   **Method 1: Reply in group**
   - Find the assignment message in the group
   - Reply to it with your text/file
   - Bot will capture your submission automatically
   
   **Method 2: Use Mini App**
   - Open the assignment in the Mini App
   - Type your answer
   - Attach files if needed
   - Click "Submit"

## Part 7: Creating Your First Quiz

### As a Teacher:

1. **Navigate to Quizzes**
   - Open the dashboard
   - Find the Quizzes section (or create a quiz interface)

2. **Create a quiz**
   ```json
   POST /api/quiz/teacher/quizzes
   {
     "class_id": "your_class_id",
     "title": "Chapter 1 Quiz",
     "description": "Test your knowledge",
     "time_limit_minutes": 30,
     "passing_score": 70
   }
   ```

3. **Add questions**
   ```json
   POST /api/quiz/teacher/questions
   {
     "quiz_id": "Q123456",
     "question_text": "What is 2+2?",
     "question_type": "multiple_choice",
     "options": [
       {"id": "a", "text": "3"},
       {"id": "b", "text": "4"},
       {"id": "c", "text": "5"}
     ],
     "correct_answer": "b",
     "points": 1
   }
   ```

4. **Publish the quiz**
   ```json
   PATCH /api/quiz/teacher/quizzes/Q123456
   {
     "status": "published"
   }
   ```

### As a Student:

1. **View available quizzes**
   - Open the dashboard
   - Navigate to Quizzes
   - See all published quizzes

2. **Take a quiz**
   - Click on a quiz
   - Click "Start Quiz"
   - Answer all questions
   - Submit to see your score

## Troubleshooting

### Problem: Bot not responding

**Solution:**
- Check if bot.py is running
- Verify bot token in .env is correct
- Check internet connection
- Look for errors in the bot terminal

### Problem: Mini App won't load

**Solution:**
- Verify WEBAPP_URL in .env is correct
- Ensure server is running on port 8000
- Check if ngrok tunnel is active (for local testing)
- Make sure URL is HTTPS
- Try clearing Telegram cache

### Problem: Submissions not captured in group

**Solution:**
- Ensure bot privacy mode is disabled in BotFather
- Check if student replied to the correct message
- Verify bot is in the group and has permission to read messages
- Look for errors in bot logs

### Problem: "Authentication Failed"

**Solution:**
- If testing locally, set `DEV_SKIP_INITDATA_VALIDATION=true`
- Check if Telegram WebApp initData is being sent
- Verify server is accessible from Telegram servers (must be HTTPS)

### Problem: File upload fails

**Solution:**
- Check if `data/files/` directory exists
- Verify directory has write permissions
- Check available disk space
- Look for file size limits

## Security Checklist for Production

Before going live:

- [ ] Set `DEV_SKIP_INITDATA_VALIDATION=false`
- [ ] Implement proper HMAC validation in `server/app.py`
- [ ] Use HTTPS for all endpoints
- [ ] Keep bot token secret (never commit to git)
- [ ] Set up file upload size limits
- [ ] Implement rate limiting
- [ ] Set up backup for `data/data.json`
- [ ] Configure proper file permissions
- [ ] Set up monitoring and logging
- [ ] Test in a staging environment first

## Next Steps

Now that your LMS is set up:

1. **Customize the UI**
   - Edit `frontend/teacher.html` and `frontend/student.html`
   - Add your school logo and colors
   - Customize the welcome messages

2. **Add more features**
   - Implement grading system
   - Add discussion forums
   - Create course materials section
   - Add calendar view

3. **Integrate with existing systems**
   - Connect to student information system
   - Export grades to CSV/Excel
   - Add single sign-on (SSO)

4. **Scale up**
   - Move to a proper database (PostgreSQL, MongoDB)
   - Set up Redis for caching
   - Deploy with Docker
   - Use load balancers for high traffic

## Getting Help

- Check the [README.md](README.md) for API documentation
- Review error logs in the terminal
- Test individual components separately
- Ask questions in the community

## Additional Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [Telegram Mini Apps Guide](https://core.telegram.org/bots/webapps)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python-Telegram-Bot Documentation](https://python-telegram-bot.readthedocs.io/)

---

Good luck with your LMS! 🎓

