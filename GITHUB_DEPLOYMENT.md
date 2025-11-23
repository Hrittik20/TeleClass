# GitHub Deployment Guide

Simple guide to deploy your Telegram LMS from GitHub.

## 🚀 Quick Deploy (3 Steps)

### Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Telegram LMS"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Server

**On your server (DigitalOcean, AWS, etc.):**

```bash
# Install Python
sudo apt update
sudo apt install python3 python3-pip python3-venv git -y

# Clone your repository
cd /var/www/
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git lms
cd lms

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
```

**Add to .env:**
```env
NOETICA_BOT_TOKEN=your_bot_token_here
WEBAPP_URL=https://your-domain.com/miniapp
DEV_SKIP_INITDATA_VALIDATION=false
```

### Step 3: Start Services

```bash
# Make startup script executable
chmod +x deploy.sh

# Run deployment script
./deploy.sh
```

That's it! Your LMS is running! 🎉

---

## 📋 Detailed Steps

### A. Prepare Repository

#### 1. Clean Up Sensitive Files

**Before pushing to GitHub:**

```bash
# Make sure .env is in .gitignore (already done)
cat .gitignore | grep .env

# Remove any accidentally committed .env
git rm --cached .env 2>/dev/null || true

# Remove data directory (contains user data)
git rm -r --cached data/ 2>/dev/null || true
```

#### 2. Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `telegram-lms` (or your choice)
3. Description: "Learning Management System for Telegram"
4. Privacy: Choose Public or Private
5. Don't initialize with README (you already have one)
6. Click "Create repository"

#### 3. Push Code

```bash
# If starting fresh
git init
git add .
git commit -m "Initial commit: Telegram LMS"

# Add remote (replace with your GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/telegram-lms.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

### B. Server Setup

#### Option 1: DigitalOcean (Recommended for beginners)

**1. Create Droplet**
- Sign up at [digitalocean.com](https://www.digitalocean.com/)
- Create new Droplet
- Choose: Ubuntu 22.04 LTS
- Plan: Basic - $6/month (1GB RAM)
- Add SSH key
- Create Droplet

**2. Connect to Server**
```bash
ssh root@your_droplet_ip
```

**3. Initial Setup**
```bash
# Update system
apt update && apt upgrade -y

# Install required packages
apt install python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx -y

# Create application user
adduser lms --disabled-password --gecos ""
usermod -aG sudo lms

# Switch to application user
su - lms
```

#### Option 2: AWS EC2

**1. Launch Instance**
- Go to EC2 Dashboard
- Launch Instance
- Choose Ubuntu Server 22.04 LTS
- Instance type: t2.micro (free tier) or t2.small
- Configure security group:
  - SSH (22) - Your IP
  - HTTP (80) - Anywhere
  - HTTPS (443) - Anywhere
- Launch

**2. Connect**
```bash
ssh -i your-key.pem ubuntu@your_instance_ip
```

**3. Setup**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx -y
```

#### Option 3: Any Linux Server

**Requirements:**
- Ubuntu 20.04+ or Debian 11+
- Root or sudo access
- Open ports: 80, 443

**Setup:**
```bash
# Update and install
sudo apt update
sudo apt install python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx -y
```

---

### C. Deploy Application

#### 1. Clone Repository

```bash
# Create application directory
sudo mkdir -p /var/www/lms
sudo chown $USER:$USER /var/www/lms
cd /var/www

# Clone from GitHub
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git lms
cd lms

# If private repository, you'll need to authenticate:
# Option A: Use personal access token
# Option B: Use SSH key (add to GitHub)
```

#### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed!')"
python -c "import telegram; print('Telegram bot installed!')"
```

#### 3. Configure Environment

```bash
# Create .env file
nano .env
```

**Add this content:**
```env
NOETICA_BOT_TOKEN=your_bot_token_from_botfather
WEBAPP_URL=https://your-domain.com/miniapp
DEV_SKIP_INITDATA_VALIDATION=false
```

Save with `Ctrl+X`, then `Y`, then `Enter`

#### 4. Create Data Directories

```bash
# Create data directories
mkdir -p data/files

# Set permissions
chmod 755 data
chmod 755 data/files
```

#### 5. Test the Application

```bash
# Test API server
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000 &

# Test bot
python bot/bot.py &

# Check if running
curl http://localhost:8000/api/health

# Should return: {"ok":true}

# Stop test processes
killall python3
```

---

### D. Set Up Services

#### 1. Create Systemd Service for API

```bash
sudo nano /etc/systemd/system/lms-api.service
```

**Add:**
```ini
[Unit]
Description=Noetica LMS API Server
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/var/www/lms
Environment="PATH=/var/www/lms/venv/bin"
ExecStart=/var/www/lms/venv/bin/uvicorn server.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Replace `YOUR_USERNAME` with your actual username** (run `whoami` to check)

#### 2. Create Systemd Service for Bot

```bash
sudo nano /etc/systemd/system/lms-bot.service
```

**Add:**
```ini
[Unit]
Description=Noetica LMS Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/var/www/lms
Environment="PATH=/var/www/lms/venv/bin"
ExecStart=/var/www/lms/venv/bin/python bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services (start on boot)
sudo systemctl enable lms-api
sudo systemctl enable lms-bot

# Start services
sudo systemctl start lms-api
sudo systemctl start lms-bot

# Check status
sudo systemctl status lms-api
sudo systemctl status lms-bot

# View logs
sudo journalctl -u lms-api -f
sudo journalctl -u lms-bot -f
```

---

### E. Set Up Nginx & SSL

#### 1. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/lms
```

**Add:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 10M;
}
```

**Replace `your-domain.com` with your actual domain**

#### 2. Enable Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/lms /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

#### 3. Get SSL Certificate (HTTPS)

```bash
# Make sure DNS is pointed to your server first!
# Then run:

sudo certbot --nginx -d your-domain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose to redirect HTTP to HTTPS (option 2)

# Certificate will auto-renew
```

#### 4. Test HTTPS

```bash
# Visit in browser:
https://your-domain.com/api/health

# Should show: {"ok":true}
```

---

### F. Update Bot Configuration

#### 1. Update BotFather

1. Open Telegram and go to [@BotFather](https://t.me/BotFather)
2. Send `/mybots`
3. Select your bot
4. Click **Bot Settings** → **Menu Button**
5. Enter your Mini App URL: `https://your-domain.com/miniapp`
6. Done!

#### 2. Test Everything

**In Telegram:**
1. Search for your bot
2. Send `/start` - should get welcome message
3. Send `/dashboard` - should see button
4. Click button - Mini App should load
5. Create a test group and add bot
6. Send `/init_class` in group
7. Create an assignment
8. Test submission

---

## 🔄 Updating Your Application

### When you make changes to code:

```bash
# On your local machine
git add .
git commit -m "Description of changes"
git push

# On your server
cd /var/www/lms
git pull

# Restart services
sudo systemctl restart lms-api
sudo systemctl restart lms-bot
```

### Automatic Updates (Optional)

Create `/var/www/lms/update.sh`:

```bash
#!/bin/bash
cd /var/www/lms
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart lms-api
sudo systemctl restart lms-bot
echo "Updated and restarted!"
```

Make executable:
```bash
chmod +x update.sh
```

Now you can update with:
```bash
./update.sh
```

---

## 🛠️ Useful Commands

### Service Management
```bash
# Start services
sudo systemctl start lms-api lms-bot

# Stop services
sudo systemctl stop lms-api lms-bot

# Restart services
sudo systemctl restart lms-api lms-bot

# Check status
sudo systemctl status lms-api lms-bot

# View logs
sudo journalctl -u lms-api -f
sudo journalctl -u lms-bot -f
```

### Application Management
```bash
# Update from GitHub
cd /var/www/lms && git pull

# Check what changed
git log --oneline -5

# View bot output
tail -f /var/log/syslog | grep python

# Check API
curl http://localhost:8000/api/health
```

### Server Management
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep python

# Monitor system resources
htop
```

---

## 🐛 Troubleshooting

### Services won't start

```bash
# Check logs
sudo journalctl -u lms-api -n 50
sudo journalctl -u lms-bot -n 50

# Check if ports are in use
sudo netstat -tulpn | grep :8000

# Try running manually
cd /var/www/lms
source venv/bin/activate
python bot/bot.py
```

### Git pull fails

```bash
# Discard local changes
git stash

# Pull again
git pull

# Or reset to remote
git fetch origin
git reset --hard origin/main
```

### Permission errors

```bash
# Fix ownership
sudo chown -R $USER:$USER /var/www/lms

# Fix permissions
chmod -R 755 /var/www/lms
chmod 600 /var/www/lms/.env
```

### Database issues

```bash
# Backup current data
cp /var/www/lms/data/data.json /var/www/lms/data/data.json.backup

# Check if valid JSON
python3 -m json.tool /var/www/lms/data/data.json

# Reset if corrupted
rm /var/www/lms/data/data.json
sudo systemctl restart lms-api
```

---

## 🔒 Security Checklist

- [ ] .env file is NOT in git repository
- [ ] SSH key authentication enabled (no password login)
- [ ] Firewall configured (ufw or similar)
- [ ] SSL certificate installed and auto-renewing
- [ ] Regular backups set up
- [ ] Services running as non-root user
- [ ] Fail2ban installed (optional but recommended)

---

## 💰 Cost Estimate

**DigitalOcean Basic Droplet:**
- $6/month (1GB RAM) - Good for 50-100 users
- $12/month (2GB RAM) - Good for 200-500 users

**AWS EC2:**
- t2.micro (free tier for 1 year)
- t2.small - ~$17/month

**Domain Name:**
- ~$10-15/year (from Namecheap, Google Domains, etc.)

**SSL Certificate:**
- FREE (Let's Encrypt)

**Total:** ~$6-17/month + $10/year for domain

---

## 📚 Next Steps

1. **Deploy to production** following this guide
2. **Test everything** thoroughly
3. **Set up backups** (see below)
4. **Invite pilot users** (1-2 classes)
5. **Gather feedback** and improve
6. **Launch to everyone!**

### Setting Up Backups

Create `/usr/local/bin/backup-lms.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf /root/backups/lms-$DATE.tar.gz \
  /var/www/lms/data/ \
  /var/www/lms/.env

# Keep only last 30 days
find /root/backups/ -name "lms-*.tar.gz" -mtime +30 -delete
```

Schedule daily:
```bash
sudo crontab -e
# Add:
0 2 * * * /usr/local/bin/backup-lms.sh
```

---

## 🎉 Success!

Your Telegram LMS is now:
- ✅ Running on a server
- ✅ Accessible via HTTPS
- ✅ Managed by systemd (auto-restart)
- ✅ Easy to update from GitHub
- ✅ Production-ready!

**Test it:** Send `/start` to your bot in Telegram!

**Questions?** Check the main [README.md](README.md) or [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

**Quick Links:**
- [GitHub](https://github.com/YOUR_USERNAME/YOUR_REPO)
- [DigitalOcean](https://www.digitalocean.com/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Telegram BotFather](https://t.me/BotFather)

