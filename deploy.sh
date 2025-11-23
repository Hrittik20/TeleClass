#!/bin/bash
# Noetica LMS - Simple Deployment Script
# This script sets up and starts the LMS on a Linux server

set -e  # Exit on error

echo "=========================================="
echo "Noetica LMS - Deployment Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root${NC}"
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Working directory: $SCRIPT_DIR"
echo ""

# Step 1: Check Python
echo -e "${YELLOW}[1/7] Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed!${NC}"
    echo "Install with: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
echo ""

# Step 2: Create virtual environment
echo -e "${YELLOW}[2/7] Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi
echo ""

# Step 3: Install dependencies
echo -e "${YELLOW}[3/7] Installing dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 4: Check .env file
echo -e "${YELLOW}[4/7] Checking configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found!${NC}"
    echo ""
    echo "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env file with your settings:${NC}"
        echo "  nano .env"
        echo ""
        echo "Required settings:"
        echo "  - NOETICA_BOT_TOKEN (from @BotFather)"
        echo "  - WEBAPP_URL (your domain)"
        echo ""
        exit 1
    else
        echo -e "${RED}.env.example not found!${NC}"
        exit 1
    fi
else
    # Check if required variables are set
    source .env
    if [ -z "$NOETICA_BOT_TOKEN" ]; then
        echo -e "${RED}✗ NOETICA_BOT_TOKEN not set in .env${NC}"
        exit 1
    fi
    if [ -z "$WEBAPP_URL" ]; then
        echo -e "${RED}✗ WEBAPP_URL not set in .env${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Configuration looks good${NC}"
fi
echo ""

# Step 5: Create data directories
echo -e "${YELLOW}[5/7] Setting up data directories...${NC}"
mkdir -p data/files
chmod 755 data
chmod 755 data/files
echo -e "${GREEN}✓ Data directories ready${NC}"
echo ""

# Step 6: Test the application
echo -e "${YELLOW}[6/7] Testing application...${NC}"
if python -c "from server.app import app; from bot.bot import TOKEN" 2>/dev/null; then
    echo -e "${GREEN}✓ Application imports successfully${NC}"
else
    echo -e "${RED}✗ Application has import errors${NC}"
    exit 1
fi
echo ""

# Step 7: Decide how to run
echo -e "${YELLOW}[7/7] Starting services...${NC}"
echo ""

# Check if systemd is available
if command -v systemctl &> /dev/null; then
    echo "Systemd detected. Install as system service?"
    echo "This requires sudo and will run the LMS on system startup."
    echo ""
    read -p "Install as system service? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Install as systemd service
        echo "Installing systemd services..."
        
        # Get current user
        CURRENT_USER=$(whoami)
        
        # Create API service
        sudo tee /etc/systemd/system/lms-api.service > /dev/null << EOF
[Unit]
Description=Noetica LMS API Server
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=$SCRIPT_DIR/venv/bin"
ExecStart=$SCRIPT_DIR/venv/bin/uvicorn server.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        # Create Bot service
        sudo tee /etc/systemd/system/lms-bot.service > /dev/null << EOF
[Unit]
Description=Noetica LMS Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=$SCRIPT_DIR/venv/bin"
ExecStart=$SCRIPT_DIR/venv/bin/python bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        # Enable and start services
        sudo systemctl daemon-reload
        sudo systemctl enable lms-api lms-bot
        sudo systemctl restart lms-api lms-bot
        
        echo ""
        echo -e "${GREEN}✓ Services installed and started!${NC}"
        echo ""
        echo "Useful commands:"
        echo "  sudo systemctl status lms-api lms-bot  - Check status"
        echo "  sudo systemctl restart lms-api lms-bot - Restart services"
        echo "  sudo systemctl stop lms-api lms-bot    - Stop services"
        echo "  sudo journalctl -u lms-api -f          - View API logs"
        echo "  sudo journalctl -u lms-bot -f          - View Bot logs"
        echo ""
    else
        # Run in terminal
        echo "Starting services in background..."
        echo ""
        
        # Kill any existing processes
        pkill -f "uvicorn server.app:app" 2>/dev/null || true
        pkill -f "python.*bot/bot.py" 2>/dev/null || true
        
        # Start API server
        nohup venv/bin/uvicorn server.app:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
        API_PID=$!
        
        # Wait a bit
        sleep 2
        
        # Start bot
        nohup venv/bin/python bot/bot.py > logs/bot.log 2>&1 &
        BOT_PID=$!
        
        echo -e "${GREEN}✓ Services started!${NC}"
        echo ""
        echo "API Server PID: $API_PID"
        echo "Bot PID: $BOT_PID"
        echo ""
        echo "Logs:"
        echo "  tail -f logs/api.log  - API logs"
        echo "  tail -f logs/bot.log  - Bot logs"
        echo ""
        echo "To stop:"
        echo "  kill $API_PID $BOT_PID"
        echo ""
    fi
else
    # No systemd, run in terminal
    echo "Starting services in terminal..."
    echo ""
    
    # Create logs directory
    mkdir -p logs
    
    # Start API server in background
    venv/bin/uvicorn server.app:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
    API_PID=$!
    
    sleep 2
    
    # Start bot in background
    venv/bin/python bot/bot.py > logs/bot.log 2>&1 &
    BOT_PID=$!
    
    echo -e "${GREEN}✓ Services started!${NC}"
    echo ""
    echo "API Server PID: $API_PID"
    echo "Bot PID: $BOT_PID"
    echo ""
    echo "Logs:"
    echo "  tail -f logs/api.log"
    echo "  tail -f logs/bot.log"
    echo ""
fi

# Final checks
echo ""
echo "=========================================="
echo "Checking if services are running..."
echo "=========================================="
echo ""

sleep 3

# Check API
if curl -s http://localhost:8000/api/health | grep -q "ok"; then
    echo -e "${GREEN}✓ API Server is running${NC}"
    echo "  URL: http://localhost:8000"
    echo "  Docs: http://localhost:8000/docs"
else
    echo -e "${RED}✗ API Server is not responding${NC}"
    echo "  Check logs: tail -f logs/api.log"
fi

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test in Telegram: Send /start to your bot"
echo "2. Create a test group and add your bot"
echo "3. Run /init_class in the group"
echo "4. Send /dashboard to open the Mini App"
echo ""
echo "For production setup with Nginx and SSL:"
echo "  See: GITHUB_DEPLOYMENT.md"
echo ""
echo -e "${GREEN}Happy teaching! 📚✨${NC}"

