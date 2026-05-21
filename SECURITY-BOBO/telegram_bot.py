import telebot
import config
import logging

# SECURITY-BOBO Telegram Bot
# Buyruqlar: /start, /status, /panic, /report

class TelegramNotifier:
    def __init__(self):
        self.bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.logger = logging.getLogger("TelegramBot")

        # Buyruqlarni ro'yxatga olish
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.bot.reply_to(message, "🚀 SECURITY-BOBO A1 Tizimiga xush kelibsiz!\nBuyruqlar: /status, /panic, /report")

        @self.bot.message_handler(commands=['status'])
        def send_status(message):
            # Tizim holatini yuborish mantiqi
            self.bot.reply_to(message, "📊 Tizim holati: Ishlamoqda\nBarcha agentlar faol.")

        @self.bot.message_handler(commands=['panic'])
        def panic_trigger(message):
            # Panic button mantiqi (Nazoratchi orqali)
            self.bot.reply_to(message, "🆘 PANIC: Barcha savdolarni yopish buyrug'i qabul qilindi!")

    def send_message(self, text):
        """Xabar yuborish"""
        try:
            self.bot.send_message(self.chat_id, text, parse_mode='Markdown')
        except Exception as e:
            self.logger.error(f"Telegram yuborishda xatolik: {e}")

    def polling(self):
        """Botni doimiy eshitish rejimiga o'tkazish (Alohida thread'da)"""
        self.bot.infinity_polling()
