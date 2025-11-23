# Quick Start Guide

Get your Telegram LMS up and running in 5 minutes!

## 🚀 5-Minute Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the bot token you receive

### 3. Configure

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your bot token:

```env
NOETICA_BOT_TOKEN=your_token_here
WEBAPP_URL=https://your-domain.com/miniapp
DEV_SKIP_INITDATA_VALIDATION=true  # For local testing
```

### 4. Start the Application

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Or manually:**
```bash
# Terminal 1
uvicorn server.app:app --reload

# Terminal 2
python bot/bot.py
```

### 5. Test It!

1. Open Telegram
2. Search for your bot
3. Send `/start`
4. Create a test group and add your bot
5. Send `/init_class` in the group

## 🐳 Docker Setup (Alternative)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🧪 Testing Locally

For local testing without HTTPS:

1. Install [ngrok](https://ngrok.com/):
   ```bash
   # Download from https://ngrok.com/download
   ```

2. Start ngrok:
   ```bash
   ngrok http 8000
   ```

3. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

4. Update `.env`:
   ```env
   WEBAPP_URL=https://abc123.ngrok.io/miniapp
   DEV_SKIP_INITDATA_VALIDATION=true
   ```

5. Update your bot in [@BotFather](https://t.me/BotFather):
   - `/mybots` → select your bot
   - **Bot Settings** → **Menu Button**
   - Set to: `https://abc123.ngrok.io/miniapp`

## 📱 Using the LMS

### As a Teacher

1. Send `/dashboard` to your bot
2. Click "Open LMS Dashboard"
3. Link your class (you need the group chat ID)
4. Create your first assignment
5. The assignment will be posted in your group

### As a Student

1. Get the course code from your teacher
2. Send `/dashboard` to the bot
3. Click "Open LMS Dashboard"
4. Click "Enroll in Course"
5. Enter the course code
6. View and submit assignments

## ❓ Need Help?

- 📖 Read the [full README](README.md)
- 📚 Check the [Setup Guide](SETUP_GUIDE.md)
- 🐛 [Report issues](https://github.com/your-repo/issues)

## 🎓 Next Steps

- Customize the UI in `frontend/`
- Add more question types for quizzes
- Integrate with your student information system
- Deploy to production

---

Happy teaching! 📚✨

