#!/bin/bash

# RATP Bot - Raspberry Pi Installer

set -e

# Detect current directory and user
WORKDIR=$(pwd)
CURRENT_USER=$(whoami)
VENV_PATH="$WORKDIR/venv"
PYTHON_CMD="$VENV_PATH/bin/python"

echo "🚗 RATP Bot - Installing on Raspberry Pi..."
echo "📂 Working directory: $WORKDIR"
echo "👤 User: $CURRENT_USER"

# 1. Setup Python Environment
if [ ! -d "$VENV_PATH" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# 2. Install Dependencies
echo "📦 Installing requirements..."
$VENV_PATH/bin/pip install -r requirements.txt

# 3. Check .env
if [ ! -f "$WORKDIR/.env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "   Please create it from .env.example before running the bot."
    cp .env.example .env
    echo "   Created empty .env file. Please edit it."
fi

# 4. Configure Systemd Service
echo "⚙️  Configuring Systemd Service..."

SERVICE_FILE="/etc/systemd/system/ratp-bot.service"
TIMER_FILE="/etc/systemd/system/ratp-bot.timer"

# Read template and substitute variables
# Escaping path slashes for sed
ESCAPED_WORKDIR=$(echo $WORKDIR | sed 's/\//\\\//g')
ESCAPED_PYTHON_CMD=$(echo $PYTHON_CMD | sed 's/\//\\\//g')

# We use temporary files to avoid permission issues with redirection requiring sudo
# but actually we can just generate the content and then use sudo tee
sed "s/{{WORKDIR}}/$ESCAPED_WORKDIR/g; s/{{PYTHON_CMD}}/$ESCAPED_PYTHON_CMD/g; s/{{USER}}/$CURRENT_USER/g" systemd/ratp-bot.service.template > ratp-bot.service.generated

echo "   Installing service file to $SERVICE_FILE (asking for sudo)..."
sudo cp ratp-bot.service.generated $SERVICE_FILE
rm ratp-bot.service.generated

# 5. Configure Systemd Timer
echo "⏰ Configuring Systemd Timer..."
echo "   Installing timer file to $TIMER_FILE (asking for sudo)..."
sudo cp systemd/ratp-bot.timer $TIMER_FILE

# 6. Enable and Start
echo "🚀 Enabling and starting timer..."
sudo systemctl daemon-reload
sudo systemctl enable ratp-bot.timer
sudo systemctl start ratp-bot.timer

echo ""
echo "✅ Installation complete!"
echo "   The bot is now scheduled to run Mon-Fri at 08:00 and 17:50."
echo "   To check status: sudo systemctl status ratp-bot.timer"
echo "   To check logs:   sudo journalctl -u ratp-bot.service -f"
echo "   To test now:     sudo systemctl start ratp-bot.service"
