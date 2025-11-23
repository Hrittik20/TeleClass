# 🚀 Getting Started with Your Telegram LMS

**Welcome!** Your Telegram Learning Management System is ready to deploy.

## ⚡ Quick Start (Choose Your Path)

### 🌟 Recommended: GitHub → Server Deployment

**This is the simplest way!**

1. **Push to GitHub** (5 minutes)
2. **Deploy to Server** (15 minutes)
3. **Start Teaching!**

👉 **Follow:** [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md)

---

## 📖 What This Is

A complete **Learning Management System** that runs inside **Telegram**:

- ✅ Teachers create assignments
- ✅ Students submit work
- ✅ Automatic quizzes with grading
- ✅ File uploads
- ✅ Progress tracking
- ✅ Works on all devices (phone, tablet, desktop)
- ✅ **No app to install** - runs in Telegram!

---

## 📋 Before You Start

You need:

1. **Telegram Bot Token** 
   - Get from [@BotFather](https://t.me/BotFather) (free, 2 minutes)

2. **A Server** (choose one):
   - DigitalOcean: $6/month ([sign up](https://www.digitalocean.com/))
   - AWS: Free tier for 1 year ([sign up](https://aws.amazon.com/free/))
   - Any Linux server with Ubuntu 20.04+

3. **A Domain Name** (optional but recommended):
   - Namecheap, Google Domains, etc. (~$10/year)
   - Or use server IP address for testing

---

## 🎯 Deployment Steps

### Step 1: Push Code to GitHub

```bash
# In this directory (Miniapp)
git init
git add .
git commit -m "Initial commit - Telegram LMS"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

📖 **Detailed instructions:** [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md) - Section A

---

### Step 2: Deploy to Server

**On your server (via SSH):**

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv git nginx certbot -y

# Clone your repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git lms
cd lms

# Run deployment script
chmod +x deploy.sh
./deploy.sh
```

The script will:
- ✅ Set up Python environment
- ✅ Install dependencies
- ✅ Create data directories
- ✅ Start services

📖 **Detailed instructions:** [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md) - Section B & C

---

### Step 3: Set Up HTTPS (Production)

```bash
# Configure Nginx
sudo nano /etc/nginx/sites-available/lms
# (Copy config from GITHUB_DEPLOYMENT.md)

# Get SSL certificate (FREE)
sudo certbot --nginx -d your-domain.com

# Done! Your site is now HTTPS
```

📖 **Detailed instructions:** [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md) - Section E

---

### Step 4: Configure Bot

1. Open [@BotFather](https://t.me/BotFather) in Telegram
2. Send `/mybots` → Select your bot
3. **Bot Settings** → **Menu Button**
4. Set URL: `https://your-domain.com/miniapp`
5. Done!

---

### Step 5: Test!

1. Search for your bot in Telegram
2. Send `/start`
3. Create a test group, add your bot
4. Run `/init_class` in the group
5. Send `/dashboard` to open Mini App
6. Create your first assignment!

🎉 **You're live!**

---

## 📚 Documentation

Pick what you need:

| Document | When to Read | Time |
|----------|-------------|------|
| **[GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md)** | ⭐ **Start here!** | 20 min |
| **[QUICKSTART.md](QUICKSTART.md)** | Local testing | 5 min |
| **[README.md](README.md)** | Understand features | 15 min |
| **[API_REFERENCE.md](API_REFERENCE.md)** | Building integrations | Reference |
| **[FEATURES.md](FEATURES.md)** | See what it can do | Reference |
| **[SETUP_GUIDE.md](SETUP_GUIDE.md)** | Detailed setup help | 30 min |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Technical details | 20 min |
| **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** | Production launch | 2 hours |

---

## 🆘 Common Issues

### "Bot not responding"

**Check if bot is running:**
```bash
sudo systemctl status lms-bot
sudo journalctl -u lms-bot -f
```

**Restart it:**
```bash
sudo systemctl restart lms-bot
```

---

### "Mini App won't load"

**Check these:**
1. Is server running? `sudo systemctl status lms-api`
2. Is HTTPS working? Visit `https://your-domain.com/api/health`
3. Did you update BotFather with correct URL?
4. Is `WEBAPP_URL` correct in `.env` file?

---

### "Can't connect to server"

**Check these:**
1. Is firewall open? `sudo ufw status`
2. Are ports open? `sudo netstat -tulpn | grep :80`
3. Is Nginx running? `sudo systemctl status nginx`

---

### "Git push failed"

**First time pushing:**
```bash
# Set up git identity
git config --global user.email "you@example.com"
git config --global user.name "Your Name"

# Try again
git push
```

---

## 💡 Tips for Success

### 1. Start Small
- Test with 1-2 classes first
- Gather feedback
- Fix issues
- Then scale up

### 2. Backup Your Data
```bash
# On server
cp /var/www/lms/data/data.json ~/backup/
```

### 3. Update Regularly
```bash
# Pull latest code
cd /var/www/lms
git pull
sudo systemctl restart lms-api lms-bot
```

### 4. Monitor Your System
```bash
# Check logs
sudo journalctl -u lms-api -f
sudo journalctl -u lms-bot -f

# Check disk space
df -h

# Check memory
free -h
```

---

## 🎓 Real-World Example

**Scenario:** High school teacher with 3 classes

### Day 1: Deploy
- Push code to GitHub: **10 minutes**
- Set up DigitalOcean server: **15 minutes**
- Deploy and configure: **20 minutes**
- Test everything: **15 minutes**

**Total setup time: 1 hour**

### Day 2: First Class
- Create group for Class A
- Run `/init_class`
- Share course code with students
- Create first assignment
- Students start submitting

**Time to first assignment: 5 minutes**

### Week 1: Regular Use
- 3 assignments per class
- 100+ submissions
- 2 quizzes with auto-grading
- All running smoothly

**Total cost: $6/month**

---

## 💰 Costs

### Minimum Setup
- **Server:** $6/month (DigitalOcean Basic)
- **Domain:** $10/year (optional)
- **SSL:** FREE (Let's Encrypt)
- **Total:** ~$7/month

### Can Handle
- ✅ 100+ students
- ✅ 10+ classes
- ✅ 1000s of submissions
- ✅ Unlimited assignments & quizzes

---

## 🔐 Security Notes

**Before going live:**

1. ✅ Use HTTPS (required for Telegram)
2. ✅ Set `DEV_SKIP_INITDATA_VALIDATION=false` in `.env`
3. ✅ Never commit `.env` to GitHub (already in `.gitignore`)
4. ✅ Keep your bot token secret
5. ✅ Set up automatic backups

---

## 🎉 You're Ready!

**Next action:** Open [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md) and follow Step 1!

---

## 📞 Need Help?

**Check the docs first:**
- All guides are in this folder
- Search for your error message
- Read the troubleshooting sections

**Still stuck?**
- Check service logs: `sudo journalctl -u lms-api -f`
- Verify configuration: `cat .env`
- Test API: `curl http://localhost:8000/api/health`

---

## 📊 What You'll Have

After deployment:

```
✅ Telegram Bot responding to commands
✅ Mini App loading in Telegram
✅ Teachers can create classes
✅ Students can enroll with codes
✅ Assignments can be posted
✅ Submissions are captured
✅ Quizzes work with auto-grading
✅ Everything backed up
✅ HTTPS enabled
✅ Auto-restart on failure
✅ Easy to update from GitHub
```

---

## 🚀 Let's Go!

1. Read [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md)
2. Push to GitHub
3. Deploy to server
4. Start teaching!

**Time to production: ~1 hour**

**Questions?** All answers are in the documentation! 📚

---

**Ready? Open [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md) now!** →

