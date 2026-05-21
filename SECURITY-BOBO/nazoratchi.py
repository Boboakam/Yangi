import logging
import config
import datetime
from telegram_bot import TelegramNotifier

# NAZORATCHI Agent (Rules 25-30)
class Nazoratchi:
    def __init__(self, professor, titan, boss, database):
        self.professor = professor
        self.titan = titan
        self.boss = boss
        self.db = database
        self.notifier = TelegramNotifier()
        self.logger = logging.getLogger("Nazoratchi")
        self.last_heartbeat = datetime.datetime.now()

    def check_heartbeat(self):
        """Rule 27: Heartbeat Report"""
        now = datetime.datetime.now()
        if (now - self.last_heartbeat).total_seconds() > config.HEARTBEAT_INTERVAL * 3600:
            open_pos = self.db.get_open_positions()
            msg = f"💓 *HEARTBEAT REPORT*\nHolat: FAOL\nOchiq pozitsiyalar: {len(open_pos)}"
            self.notifier.send_message(msg)
            self.last_heartbeat = now

    def evolve_logic(self):
        """Rule 29: Evolutionary Logic Override"""
        # Agar bozor "CHOPPY" bo'lsa, TQI thresholdni oshirish
        # Bu yerda Professorning parametrlarini dinamik o'zgartirish mumkin
        self.logger.info("🧠 Evolutionary Logic: Bozor tahlil qilinmoqda...")
        pass

    def verify_absolute_facts(self, symbol, side, price):
        """Rule 30: Absolute Fact Verification"""
        # Kirishdan oldin narx real ekanligini qayta tekshirish
        real_price = self.professor.binance.get_ticker(symbol)
        if abs(real_price - price) / price > 0.01:
            self.logger.error(f"❌ Fact Verification Failed: Price slippage too high for {symbol}")
            return False
        return True

    def handle_panic(self):
        """Rule 26: Panic Triggered from UI/Telegram"""
        self.boss.close_all_on_emergency()
