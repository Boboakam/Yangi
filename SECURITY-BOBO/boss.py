import config
import logging
import time
from telegram_bot import TelegramNotifier

# BOSS Agent (Boshqaruvchi & Qutqaruvchi)
# Pozitsiyalarni nazorat qiladi va Auto-Resume funksiyasini bajaradi

class Boss:
    def __init__(self, binance_client, database):
        self.binance = binance_client
        self.db = database
        self.notifier = TelegramNotifier()
        self.logger = logging.getLogger("Boss")

    def auto_resume(self):
        """Dastur qayta ishga tushganda Binance'dagi ochiq pozitsiyalarni bazaga muvofiqlashtirish"""
        self.logger.info("🔄 Auto-Resume jarayoni boshlandi...")
        try:
            active_binance_positions = self.binance.get_open_positions()

            if not active_binance_positions:
                self.logger.info("✅ Binance'da ochiq pozitsiyalar yo'q.")
                return

            for pos in active_binance_positions:
                symbol = pos['symbol']
                amount = float(pos['contracts'])
                side = 'BUY' if pos['side'] == 'long' else 'SELL'
                entry_price = float(pos['entryPrice'])

                self.logger.info(f"🔎 Tiklanmoqda: {symbol} {side} {amount}")
                # Bazada bormi tekshirish
                db_pos = self.db.cursor.execute("SELECT * FROM positions WHERE symbol=? AND status='OPEN'", (symbol,)).fetchone()
                if not db_pos:
                    # Agar bazada bo'lmasa, yangi qo'shish (Auto-Discovery)
                    sl = entry_price * 0.98 if side == 'BUY' else entry_price * 1.02
                    tp = entry_price * 1.05 if side == 'BUY' else entry_price * 0.95
                    self.db.save_position(symbol, side, amount, entry_price, sl, tp)
                    self.logger.info(f"💾 {symbol} bazaga qo'shildi.")

            self.notifier.send_message("🔄 *Auto-Resume:* Tizim tiklandi va ochiq pozitsiyalarni nazoratga oldi.")
        except Exception as e:
            self.logger.error(f"Auto-Resume xatoligi: {e}")

    def monitor_positions(self):
        """Ochiq pozitsiyalarni monitoring qilish (Trailing Stop, Break-Even, Partial TP)"""
        try:
            open_db_positions = self.db.get_open_positions()
            if not open_db_positions:
                return

            for pos in open_db_positions:
                # pos: (id, symbol, side, amount, entry_price, sl, tp, status, timestamp)
                p_id, symbol, side, amount, entry_price, sl, tp, status, ts = pos

                curr_price = self.binance.get_ticker(symbol)
                if not curr_price: continue

                # 1. Take Profit yoki Stop Loss tekshirish
                is_closed = False
                pnl = 0
                if side == 'BUY':
                    if curr_price >= tp:
                        self.logger.info(f"🎯 TP urildi: {symbol}")
                        is_closed = True
                        pnl = (tp - entry_price) * amount
                    elif curr_price <= sl:
                        self.logger.info(f"🛑 SL urildi: {symbol}")
                        is_closed = True
                        pnl = (sl - entry_price) * amount
                else: # SELL
                    if curr_price <= tp:
                        self.logger.info(f"🎯 TP urildi: {symbol}")
                        is_closed = True
                        pnl = (entry_price - tp) * amount
                    elif curr_price >= sl:
                        self.logger.info(f"🛑 SL urildi: {symbol}")
                        is_closed = True
                        pnl = (entry_price - sl) * amount

                if is_closed:
                    # Binance da yopish orderini yuborish
                    close_side = 'SELL' if side == 'BUY' else 'BUY'
                    self.binance.open_order(symbol, close_side.lower(), amount)
                    self.db.close_position(symbol)
                    self.notifier.send_message(f"🔴 *POZITSIYA YOPIULDI*\nCoin: {symbol}\nPnL: {pnl:.2f} USDT")

                # 2. TRAILING STOP mantiqi (Soddalashtirilgan)
                # Agar narx foyda tomonga ketsa, SL ni ham surish
                if not is_closed:
                    if side == 'BUY' and curr_price > entry_price * 1.02:
                        new_sl = curr_price * 0.99
                        if new_sl > sl:
                            # Bazada yangilash
                            self.db.cursor.execute("UPDATE positions SET sl=? WHERE id=?", (new_sl, p_id))
                            self.db.conn.commit()
                            self.logger.info(f"📈 {symbol} Trailing SL surildi: {new_sl}")
                    elif side == 'SELL' and curr_price < entry_price * 0.98:
                        new_sl = curr_price * 1.01
                        if new_sl < sl:
                            self.db.cursor.execute("UPDATE positions SET sl=? WHERE id=?", (new_sl, p_id))
                            self.db.conn.commit()
                            self.logger.info(f"📉 {symbol} Trailing SL surildi: {new_sl}")

        except Exception as e:
            self.logger.error(f"Monitoring xatoligi: {e}")

    def close_all_on_emergency(self):
        """Favqulodda holatda hammasini yopish"""
        try:
            active_positions = self.binance.get_open_positions()
            for pos in active_positions:
                symbol = pos['symbol']
                amount = float(pos['contracts'])
                side = 'SELL' if pos['side'] == 'long' else 'BUY'
                self.binance.open_order(symbol, side.lower(), amount)
                self.db.close_position(symbol)
                self.logger.info(f"⚠️ Favqulodda yopildi: {symbol}")
            self.notifier.send_message("🆘 *EMERGENCY:* Barcha pozitsiyalar favqulodda yopildi!")
        except Exception as e:
            self.logger.error(f"Emergency close xatoligi: {e}")
