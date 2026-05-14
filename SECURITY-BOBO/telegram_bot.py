import requests
import config
import logging

# Telegram Notifier Moduli
# Telegram Bot API orqali O'zbek tilida xabarlar yuboradi

class TelegramNotifier:
    def __init__(self):
        self.token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.logger = logging.getLogger("TelegramBot")

    def send_message(self, text):
        """Xabar yuborish"""
        if not self.token or not self.chat_id:
            self.logger.warning("Telegram sozlamalari topilmadi.")
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Telegramga xabar yuborishda xatolik: {e}")
            return False
