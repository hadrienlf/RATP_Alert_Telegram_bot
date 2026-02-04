# 🚇 RATP Monitor Bot

A simple, robust Python bot that monitors public transport traffic in Paris (Île-de-France) and sends **Telegram** notifications.
Designed to run automatically via **GitHub Actions** (free) or locally on your machine.

## ✨ Features

- **Smart Filtering**: 
  - Ignores "Elevator" failures (Ascenseurs).
  - Ignores future planned works (not active yet).
  - Ignores simple "Information" messages (e.g., sports events).
  - **Only alerts you on active, real traffic disruptions.**
- **Multi-Line Support**: Monitors **Metro 1**, **Metro 13**, and **RER E** by default (easy to customize).
- **Silent / Verbose Modes**:
  - **Cron Mode (Auto)**: Remains silent if traffic is normal. Alerts only on problems.
  - **Manual Mode**: Confirms "✅ Trafic normal" if everything is fine (prefixed with `(TEST)`).
- **Robustness**: Automatic retries on API failure.

---

## 🛠️ Prerequisites

You need 3 keys to make it work:

1.  **IDFM / Navitia API Key**:
    - Create an account on [Prim Île-de-France Mobilités](https://prim.iledefrance-mobilites.fr/).
    - Get your API key (it's free).
2.  **Telegram Bot Token**:
    - Talk to [@BotFather](https://t.me/botfather) on Telegram.
    - Create a new bot and copy the **Token**.
3.  **Telegram Chat ID**:
    - Send a message to your new bot.
    - Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in your browser.
    - Look for `"chat": {"id": 123456789}`. That number is your **Chat ID**.

---

## 🚀 Setup on GitHub (Automatic)

**Goal**: The bot runs automatically every day at **08:00** and **17:50** (Paris time) to alert you before your commute.

1.  **Fork** this repository to your own GitHub account.
2.  Go to your forked repository's **Settings**.
3.  Navigate to **Secrets and variables** > **Actions**.
4.  Click **New repository secret** and add these 3 secrets (using the values from Prerequisites):
    - `API_KEY_IDFM`
    - `TELEGRAM_TOKEN`
    - `CHAT_ID`
5.  **Done!**
    - To test immediately: Go to the **Actions** tab, select **RATP_Monitor_Cron**, and click **Run workflow**.

---

## 💻 Local Usage (Optional)

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/<your-username>/ratp-bot.git
    cd ratp-bot
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    - Duplicate `.env.example` and rename it to `.env`.
    - Fill in your keys in the `.env` file.

4.  **Run**:
    ```bash
    python main.py
    ```

---

## ⚙️ Customization

### Changing Monitored Lines
Open `main.py` and modify the `LINES` dictionary:

```python
LINES = {
    "Ligne 1": "line:IDFM:C01371",
    "Ligne 13": "line:IDFM:C01383",
    "RER E": "line:IDFM:C01729"
}
```

*Note: You can find Line IDs via the IDFM API documentation or by exploring the API.*

### Changing Schedule
Open `.github/workflows/cron.yml` and edit the `cron` lines:
- `0 7 * * *` (07:00 UTC = 08:00 Paris Winter)
- `50 16 * * *` (16:50 UTC = 17:50 Paris Winter)
