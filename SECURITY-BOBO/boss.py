import config
import logging
import datetime
import time
from telegram_bot import TelegramNotifier
from indicators import calculate_atr, calculate_vwap

# BOSS Agent (Rules 19-24)
class Boss:
    def __init__(self, binance_client, database):
        self.binance = binance_client
        self.db = database
        self.notifier = TelegramNotifier()
        self.logger = logging.getLogger("Boss")

    def auto_resume(self):
        """Rule: Auto-Resume (Restore state)"""
        self.logger.info("🔄 Auto-Resume boshlandi...")
        positions = self.binance.get_open_positions()
        for pos in positions:
            symbol = pos['symbol']
            side = 'BUY' if pos['side'] == 'long' else 'SELL'
            amount = float(pos['contracts'])
            entry_price = float(pos['entryPrice'])

            # Bazada bormi tekshirish
            db_pos = self.db.cursor.execute("SELECT * FROM positions WHERE symbol=? AND status='OPEN'", (symbol,)).fetchone()
            if not db_pos:
                sl = entry_price * 0.98 if side == 'BUY' else entry_price * 1.02
                tp = entry_price * 1.05 if side == 'BUY' else entry_price * 0.95
                self.db.save_position(symbol, side, amount, entry_price, sl, tp)
        self.notifier.send_message(config.STATUS_MESSAGES["AUTO_RESUME"])

    def monitor_positions(self):
        """Pozitsiya boshqaruvi (Rules 19-24)"""
        open_positions = self.db.get_open_positions()
        if not open_positions: return

        for pos in open_positions:
            p_id, symbol, side, amount, entry_price, sl, tp, status, ts = pos
            curr_price = self.binance.get_ticker(symbol)
            if not curr_price: continue

            # Rule 21: Time-Decay Exit (3 soat)
            start_time = datetime.datetime.fromisoformat(ts)
            if (datetime.datetime.now() - start_time).total_seconds() > config.TIME_DECAY_EXIT_HOURS * 3600:
                pnl = (curr_price - entry_price) * amount if side == "BUY" else (entry_price - curr_price) * amount
                if pnl <= 0:
                    self._close_position(symbol, side, amount, "TIME_DECAY")
                    continue

            # Rule 19 & 24: Dynamic Trailing
            if side == "BUY" and curr_price > entry_price * 1.01:
                new_sl = max(sl, curr_price * 0.995) # Agressiv trailing
                if new_sl > sl:
                    self.db.cursor.execute("UPDATE positions SET sl=? WHERE id=?", (new_sl, p_id))
                    self.db.conn.commit()

            # Rule 22: Dynamic Scale-Out (25%, 50%)
            if side == "BUY" and curr_price >= entry_price * 1.02:
                # 25% qismini yopish (Rule implementation)
                self._partial_close(symbol, side, amount * 0.25, p_id)
                amount *= 0.75

            # TP/SL check
            if (side == "BUY" and (curr_price >= tp or curr_price <= sl)) or \
               (side == "SELL" and (curr_price <= tp or curr_price >= sl)):
                self._close_position(symbol, side, amount, "TP_SL")

    def _partial_close(self, symbol, side, partial_amount, p_id):
        """Rule 22: Scale-Out logic"""
        close_side = 'sell' if side == 'BUY' else 'buy'
        self.binance.open_order(symbol, close_side, partial_amount)
        # Bazada miqdorni yangilash
        self.db.cursor.execute("UPDATE positions SET amount = amount - ? WHERE id = ?", (partial_amount, p_id))
        self.db.conn.commit()
        self.logger.info(f"💰 Partial Close: {symbol} - {partial_amount}")

    def micro_hedge(self, symbol, side, amount):
        """Rule 23: Micro-Hedging Protocol"""
        # Agar pozitsiya SL ga juda yaqin bo'lsa, qulflash
        hedge_side = 'sell' if side == 'BUY' else 'buy'
        self.binance.open_order(symbol, hedge_side, amount * 0.5) # 50% hedge
        self.logger.info(f"🛡️ Micro-Hedge active for {symbol}")

    def _close_position(self, symbol, side, amount, reason):
        close_side = 'sell' if side == 'BUY' else 'buy'
        self.binance.open_order(symbol, close_side, amount)
        self.db.close_position(symbol)
        self.notifier.send_message(f"🔴 *POZITSIYA YOPIULDI*\nCoin: {symbol}\nSabab: {reason}")

    def close_all_on_emergency(self):
        """Rule 26: Panic / Emergency Close"""
        self.logger.warning("🚨 EMERGENCY CLOSE ALL!")
        positions = self.binance.get_open_positions()
        for pos in positions:
            symbol = pos['symbol']
            side = 'sell' if pos['side'] == 'long' else 'buy'
            amount = float(pos['contracts'])
            self.binance.open_order(symbol, side, amount)
            self.db.close_position(symbol)
        self.notifier.send_message("🆘 EMERGENCY: Barcha pozitsiyalar yopildi!")
