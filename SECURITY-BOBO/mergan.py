import config
import logging
from telegram_bot import TelegramNotifier

# MERGAN Agent (Ijrochi & Xabarchi)
# Buyruqlarni Binance'ga yuboradi va Telegram orqali xabar beradi

class Mergan:
    def __init__(self, binance_client, database):
        self.binance = binance_client
        self.db = database
        self.notifier = TelegramNotifier()
        self.logger = logging.getLogger("Mergan")

    def execute_trade(self, symbol, side, amount, signal_info):
        """Binance API orqali bozorgi kirish"""
        try:
            # Oltin uchun vaqt filtri (Mergan darajasida oxirgi blokirovka)
            if symbol == config.GOLD_SYMBOL:
                import datetime
                if datetime.datetime.now().weekday() >= 5:
                    self.logger.warning(f"❌ {symbol}: Dam olish kunida savdo qilish taqiqlangan!")
                    return None

            # Yelkani sozlash
            self.binance.set_leverage(symbol, config.LEVERAGE)

            # Order yuborish (Slippage'siz IOC ishlatiladi)
            params = {'timeInForce': 'IOC'}
            order = self.binance.open_order(symbol, side.lower(), amount, params=params)

            if order:
                self.logger.info(f"✅ {side} Order bajarildi: {symbol} x {amount}")

                # Bazaga saqlash
                entry_price = order.get('price', signal_info['price'])
                sl = entry_price * 0.98 if side == "BUY" else entry_price * 1.02
                tp = entry_price * 1.05 if side == "BUY" else entry_price * 0.95

                self.db.save_position(symbol, side, amount, entry_price, sl, tp)

                # Telegramga xabar yuborish
                msg = f"🟢 *YANGI SAVDO*\nCoin: {symbol}\nTomon: {side}\nHajm: {amount}\nNarx: {entry_price}\nTQI: {signal_info['tqi']:.2f}"
                self.notifier.send_message(msg)

                return order
        except Exception as e:
            self.logger.error(f"Ijro etishda xatolik: {e}")
            return None
