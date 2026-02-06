# 🚚 Migrating RATP Bot to Raspberry Pi

This guide explains how to move your RATP Bot from GitHub Actions to your local Raspberry Pi.

## Prerequisites

- A Raspberry Pi (or any Linux machine) with internet access.
- `git` installed on the Pi.
- Python 3 installed.

## Installation Steps (on the Pi)

1.  **Clone the Repository**
    ssh into your Pi and clone the repo:
    ```bash
    cd ~
    git clone https://github.com/hadrienlf/RATP_Alert_Telegram_bot.git
    cd RATP_Alert_Telegram_bot
    ```

2.  **Configure Environment Variables**
    Create your `.env` file:
    ```bash
    cp .env.example .env
    nano .env
    ```
    Paste your `TELEGRAM_TOKEN`, `CHAT_ID`, and `API_KEY_IDFM`.

3.  **Run the Installer**
    Making the script executable and running it:
    ```bash
    chmod +x install_pi.sh
    ./install_pi.sh
    ```
    *> This script will create a virtual environment, install dependencies, and set up the Systemd service and timer using `sudo`.*

4.  **Verify Status**
    Check that the timer is active:
    ```bash
    systemctl status ratp-bot.timer
    ```
    You should see `Active: active (waiting)` and the next trigger time (Next Elapse).

## Managing the Bot

- **Test immediately**:
    ```bash
    sudo systemctl start ratp-bot.service
    ```
    Check the logs to see if it worked:
    ```bash
    sudo journalctl -u ratp-bot.service -f
    ```

- **Stop the schedule**:
    ```bash
    sudo systemctl stop ratp-bot.timer
    sudo systemctl disable ratp-bot.timer
    ```

- **Resume the schedule**:
    ```bash
    sudo systemctl enable ratp-bot.timer
    sudo systemctl start ratp-bot.timer
    ```

- **Update Code (Logic Only)**:
    If you just changed python code (`main.py`):
    ```bash
    git pull
    # If requirements changed:
    ./venv/bin/pip install -r requirements.txt
    ```
    (No need to restart, the next run will use the new code).

- **Update Configuration (Timer/Schedule)**:
    If you changed `systemd/ratp-bot.timer` or `.env`:
    ```bash
    git pull
    # Re-run installer to update systemd files and reload
    ./install_pi.sh
    ```
