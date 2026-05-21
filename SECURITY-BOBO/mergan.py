import config
import logging
import datetime
from telegram_bot import TelegramNotifier

# MERGAN Agent (Rules 13-18)
# Snayper, Ijro va Komissiya Optimizatsiyasi

class Mergan:
    def __init__(self, binance_client, database):
        self.binance = binance_client
        self.db = database
        self.notifier = TelegramNotifier()
        self.logger = logging.getLogger("Mergan")

    def _is_in_killzone(self):
        """Rule 14: Session Killzones (UTC)"""
        now = datetime.datetime.utcnow().hour
        london = config.SESSION_KILLZONES["LONDON"]
        ny = config.SESSION_KILLZONES["NEW_YORK"]

        if london["start"] <= now <= london["end"]: return True
        if ny["start"] <= now <= ny["end"]: return True
        return False

    def _check_spoofing(self, symbol):
        """Rule 17: Spoofing Guard"""
        book = self.binance.get_order_book(symbol)
        if not book: return False

        # Agar bid yoki ask'da birorta order juda katta bo'lsa (soxta bo'lishi mumkin)
        # Soddalashtirilgan: O'rtacha hajmdan 10 baravar katta bo'lsa
        avg_bid = sum([b[1] for b in book['bids'][:10]]) / 10
        if book['bids'][0][1] > avg_bid * 10:
            self.logger.warning("🛡️ Spoofing Guard: Soxta buyurtma aniqlandi!")
            return True
        return False

    def execute_trade(self, symbol, side, amount, signal_info):
        """Ijro mantiqi (Rules 13, 15, 16, 18)"""

        # Rule 14: Sessiya tekshiruvi
        if not self._is_in_killzone():
            self.logger.info("💤 Killzone emas. Snayper kutmoqda.")
            # Ghost mode bo'lsa kirsa bo'ladi, lekin realda yo'q

        # Rule 17: Spoofing Guard
        if self._check_spoofing(symbol):
            return None

        try:
            # Rule 18: Algorithmic Front-Running (Soddalashtirilgan: API ga tezkor so'rov)
            # CCXT enableRateLimit orqali tezlikni boshqaradi

            # Rule 13: Fee Optimizer (Limit orders)
            self.binance.set_leverage(symbol, config.LEVERAGE)

            order = self.binance.open_order(symbol, side.lower(), amount)

            if order:
                entry_price = float(order.get('price', signal_info['price']))
                # Rule 11 & 19 mantiqi uchun SL/TP ni BOSS boshqaradi,
                # lekin dastlabki qiymatlarni beramiz
                sl = entry_price * 0.99 if side == "BUY" else entry_price * 1.01
                tp = entry_price * 1.03 if side == "BUY" else entry_price * 0.97

                self.db.save_position(symbol, side, amount, entry_price, sl, tp)

                # Telegramga hisobot
                msg = (f"🎯 *SNIPER ENTRY*\n"
                       f"Coin: {symbol}\n"
                       f"Side: {side}\n"
                       f"Price: {entry_price}\n"
                       f"Hajm: {amount}\n"
                       f"TQI: {signal_info['tqi']:.2f}")
                self.notifier.send_message(msg)

                return order
        except Exception as e:
            self.logger.error(f"Mergan ijro xatoligi: {e}")
            return None
