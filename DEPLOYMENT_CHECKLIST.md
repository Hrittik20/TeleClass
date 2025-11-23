# Production Deployment Checklist

Use this checklist to ensure your Telegram LMS is production-ready.

## ☑️ Pre-Deployment

### Bot Configuration
- [ ] Create production bot with [@BotFather](https://t.me/BotFather)
- [ ] Set bot name and username
- [ ] Upload bot profile picture
- [ ] Set bot description
- [ ] Configure commands with `/setcommands`
- [ ] Disable privacy mode (for group message access)
- [ ] Set menu button URL

### Domain & SSL
- [ ] Purchase/configure domain name
- [ ] Set up DNS records
- [ ] Obtain SSL certificate (Let's Encrypt recommended)
- [ ] Test HTTPS access
- [ ] Configure SSL auto-renewal

### Server Setup
- [ ] Choose hosting provider
- [ ] Provision server (minimum 2GB RAM recommended)
- [ ] Install Python 3.8+
- [ ] Install required system packages
- [ ] Set up firewall rules
- [ ] Configure SSH access
- [ ] Set up non-root user

## ☑️ Application Configuration

### Environment Variables
- [ ] Copy `.env.example` to `.env`
- [ ] Set `NOETICA_BOT_TOKEN` with production token
- [ ] Set `WEBAPP_URL` to production domain
- [ ] Set `DEV_SKIP_INITDATA_VALIDATION=false`
- [ ] Configure any custom ports
- [ ] Set up secret keys for production

### File Structure
- [ ] Create `/var/www/lms/` directory (or your preferred location)
- [ ] Clone/upload application code
- [ ] Create `data/` directory
- [ ] Create `data/files/` directory
- [ ] Set proper file permissions (755 for dirs, 644 for files)
- [ ] Create logs directory

### Dependencies
- [ ] Create Python virtual environment
- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Test import of all modules
- [ ] Verify no missing dependencies

## ☑️ Security Hardening

### Application Security
- [ ] Implement proper HMAC validation for Telegram initData
- [ ] Add rate limiting to API endpoints
- [ ] Validate file uploads (type, size, content)
- [ ] Sanitize user inputs
- [ ] Enable CORS only for trusted origins
- [ ] Add CSRF protection
- [ ] Implement request size limits
- [ ] Add malware scanning for uploads

### Server Security
- [ ] Configure firewall (UFW, iptables, etc.)
- [ ] Open only necessary ports (80, 443, SSH)
- [ ] Disable root SSH login
- [ ] Set up fail2ban
- [ ] Configure automatic security updates
- [ ] Set up intrusion detection (optional)

### Database Security
- [ ] Restrict file permissions on `data.json` (640)
- [ ] Set up automatic backups
- [ ] Encrypt backups
- [ ] Store backups off-site
- [ ] Test backup restoration

### Secrets Management
- [ ] Never commit `.env` to git
- [ ] Use environment variables for secrets
- [ ] Rotate bot token periodically
- [ ] Use strong passwords
- [ ] Limit access to production credentials

## ☑️ Service Configuration

### Systemd Services

#### API Server Service
Create `/etc/systemd/system/lms-api.service`:
```ini
[Unit]
Description=Noetica LMS API Server
After=network.target

[Service]
Type=simple
User=lms
WorkingDirectory=/var/www/lms
Environment="PATH=/var/www/lms/venv/bin"
ExecStart=/var/www/lms/venv/bin/uvicorn server.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Bot Service
Create `/etc/systemd/system/lms-bot.service`:
```ini
[Unit]
Description=Noetica LMS Telegram Bot
After=network.target

[Service]
Type=simple
User=lms
WorkingDirectory=/var/www/lms
Environment="PATH=/var/www/lms/venv/bin"
ExecStart=/var/www/lms/venv/bin/python bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable lms-api
sudo systemctl enable lms-bot
sudo systemctl start lms-api
sudo systemctl start lms-bot
```

- [ ] Create systemd service files
- [ ] Enable services
- [ ] Start services
- [ ] Verify services are running
- [ ] Test automatic restart on failure

### Nginx Configuration

Create `/etc/nginx/sites-available/lms`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Proxy to FastAPI
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # File upload size limit
    client_max_body_size 10M;

    # Logging
    access_log /var/log/nginx/lms_access.log;
    error_log /var/log/nginx/lms_error.log;
}
```

- [ ] Install Nginx
- [ ] Create configuration file
- [ ] Enable site
- [ ] Test configuration: `nginx -t`
- [ ] Reload Nginx
- [ ] Verify HTTPS works

## ☑️ Monitoring & Logging

### Application Logging
- [ ] Configure Python logging
- [ ] Set appropriate log levels
- [ ] Set up log rotation
- [ ] Store logs in `/var/log/lms/`
- [ ] Monitor log file sizes

### System Monitoring
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure alerting for downtime
- [ ] Monitor disk space
- [ ] Monitor memory usage
- [ ] Monitor CPU usage
- [ ] Set up alerts for high resource usage

### Error Tracking
- [ ] Integrate Sentry or similar (optional)
- [ ] Configure error notifications
- [ ] Test error reporting
- [ ] Review error patterns

### Application Metrics
- [ ] Track API response times
- [ ] Monitor error rates
- [ ] Track active users
- [ ] Monitor submission volume
- [ ] Set up dashboards (Grafana, etc.)

## ☑️ Backup & Recovery

### Backup Strategy
- [ ] Automated daily backups
- [ ] Backup `data/data.json`
- [ ] Backup uploaded files
- [ ] Backup .env configuration
- [ ] Store backups off-site
- [ ] Encrypt backups
- [ ] Retain backups for 30 days

### Backup Script
Create `/usr/local/bin/lms-backup.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/lms"
APP_DIR="/var/www/lms"

mkdir -p $BACKUP_DIR

# Backup database
cp $APP_DIR/data/data.json $BACKUP_DIR/data_$DATE.json

# Backup files
tar -czf $BACKUP_DIR/files_$DATE.tar.gz $APP_DIR/data/files/

# Backup .env
cp $APP_DIR/.env $BACKUP_DIR/env_$DATE

# Delete backups older than 30 days
find $BACKUP_DIR -name "data_*.json" -mtime +30 -delete
find $BACKUP_DIR -name "files_*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "env_*" -mtime +30 -delete

# Upload to cloud (optional)
# aws s3 cp $BACKUP_DIR s3://your-bucket/lms-backups/ --recursive
```

#### Set up Cron Job
```bash
# Edit crontab
sudo crontab -e

# Add daily backup at 2 AM
0 2 * * * /usr/local/bin/lms-backup.sh
```

- [ ] Create backup script
- [ ] Make script executable
- [ ] Set up cron job
- [ ] Test backup manually
- [ ] Test restoration process

### Disaster Recovery Plan
- [ ] Document recovery procedures
- [ ] Test full system restoration
- [ ] Keep recovery docs up to date
- [ ] Train team on recovery process

## ☑️ Testing

### Functional Testing
- [ ] Test bot commands (/start, /dashboard, /init_class)
- [ ] Test class creation
- [ ] Test assignment creation
- [ ] Test file upload
- [ ] Test submission via reply
- [ ] Test submission via Mini App
- [ ] Test quiz creation and taking
- [ ] Test student enrollment
- [ ] Test export functionality

### Performance Testing
- [ ] Test with 10 concurrent users
- [ ] Test with 50 concurrent users
- [ ] Test large file uploads (5MB, 10MB)
- [ ] Test API response times (<200ms)
- [ ] Test under heavy load
- [ ] Test database performance

### Security Testing
- [ ] Test authentication bypass attempts
- [ ] Test SQL injection (N/A for JSON)
- [ ] Test XSS vulnerabilities
- [ ] Test CSRF protection
- [ ] Test file upload vulnerabilities
- [ ] Test rate limiting
- [ ] Scan for common vulnerabilities

### Browser/Device Testing
- [ ] Test on iOS Telegram
- [ ] Test on Android Telegram
- [ ] Test on Telegram Desktop
- [ ] Test on Telegram Web
- [ ] Test different screen sizes
- [ ] Test dark/light themes

## ☑️ Documentation

### Technical Documentation
- [ ] API documentation complete
- [ ] Architecture documented
- [ ] Deployment process documented
- [ ] Troubleshooting guide created
- [ ] Runbook for common issues

### User Documentation
- [ ] Teacher guide
- [ ] Student guide
- [ ] Admin guide
- [ ] FAQ section
- [ ] Video tutorials (optional)

### Operations Documentation
- [ ] Backup/restore procedures
- [ ] Monitoring procedures
- [ ] Incident response plan
- [ ] Escalation procedures
- [ ] Contact information

## ☑️ Launch Preparation

### Communication Plan
- [ ] Announce to teachers
- [ ] Schedule training sessions
- [ ] Create quick start guide
- [ ] Set up support channels
- [ ] Prepare announcement messages

### Pilot Testing
- [ ] Select pilot group (1-2 classes)
- [ ] Run pilot for 1-2 weeks
- [ ] Gather feedback
- [ ] Fix critical issues
- [ ] Refine documentation

### Support Setup
- [ ] Set up support email
- [ ] Create support Telegram group
- [ ] Train support staff
- [ ] Create ticket system (optional)
- [ ] Define response time SLAs

## ☑️ Post-Launch

### Week 1
- [ ] Monitor error rates
- [ ] Collect user feedback
- [ ] Fix critical bugs
- [ ] Update documentation
- [ ] Send usage tips

### Month 1
- [ ] Review system performance
- [ ] Analyze usage patterns
- [ ] Gather feature requests
- [ ] Plan improvements
- [ ] Optimize based on metrics

### Ongoing
- [ ] Regular security updates
- [ ] Monitor costs
- [ ] Review and update backups
- [ ] Check disk space monthly
- [ ] Review logs weekly
- [ ] Update dependencies quarterly
- [ ] Conduct security audits annually

## ☑️ Compliance & Legal

### Data Privacy
- [ ] Review data collection practices
- [ ] Create privacy policy
- [ ] Ensure GDPR compliance (if applicable)
- [ ] Ensure COPPA compliance (if under 13)
- [ ] Set up data deletion process
- [ ] Document data retention policy

### Terms of Service
- [ ] Create terms of service
- [ ] Define acceptable use policy
- [ ] Set content policies
- [ ] Define liability limits

### Educational Compliance
- [ ] Review FERPA requirements (US)
- [ ] Ensure student data protection
- [ ] Set up parental consent (if needed)
- [ ] Document education records handling

## ☑️ Performance Optimization

### Application Optimization
- [ ] Enable gzip compression
- [ ] Implement caching headers
- [ ] Optimize database queries
- [ ] Add pagination for large lists
- [ ] Lazy load images
- [ ] Minify JavaScript/CSS

### Server Optimization
- [ ] Tune Nginx settings
- [ ] Configure HTTP/2
- [ ] Set up CDN (optional)
- [ ] Enable brotli compression
- [ ] Optimize SSL handshake

### Database Optimization
- [ ] Add indexes (if migrating from JSON)
- [ ] Optimize query patterns
- [ ] Set up read replicas (if needed)
- [ ] Configure connection pooling

## 📊 Success Metrics

Define and track:
- [ ] Daily active users
- [ ] Assignment completion rate
- [ ] Average response time
- [ ] Error rate (< 1%)
- [ ] Uptime (target: 99.9%)
- [ ] User satisfaction score
- [ ] Support ticket volume

## 🚀 Ready to Launch?

Go through this checklist systematically. Don't skip steps!

**Priority Levels:**
- 🔴 Critical: Must complete before launch
- 🟡 Important: Complete within first week
- 🟢 Nice to have: Can defer to later

**Questions Before Launch:**
1. Can you restore from backup?
2. Do you know how to check logs?
3. Do you have a rollback plan?
4. Is support ready to help users?
5. Have you tested the full user journey?

If you answered "yes" to all, you're ready! 🎉

## 📞 Emergency Contacts

Keep these handy:
- Hosting provider support
- Domain registrar support
- SSL certificate support
- Your development team
- System administrator

## 📚 Additional Resources

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Systemd Documentation](https://systemd.io/)
- [Let's Encrypt](https://letsencrypt.org/)
- [OWASP Security Guidelines](https://owasp.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

**Last Updated:** Check this list before every major deployment.

**Maintained By:** [Your team name/contact]

