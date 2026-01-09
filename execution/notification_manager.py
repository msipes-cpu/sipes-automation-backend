import os
import requests
import logging

logger = logging.getLogger(__name__)

def send_telegram_alert(message: str):
    """
    Sends a message to the configured Telegram user/channel via the bot.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID") # User must provide this too, or we can look it up if we store it after /start

    if not token or not chat_id:
        logger.warning("Telegram token or Chat ID missing. Skipping alert.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")
