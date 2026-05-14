import pandas as pd
from indicators import calculate_tqi, calculate_sats_bands, detect_smc_ict
import config
import logging

# PROFESSOR Agent (Tahlil miyasi)
# Bozor ma'lumotlarini tahlil qiladi va signallar ishlab chiqadi

class Professor:
    def __init__(self, binance_client):
        self.binance = binance_client
        self.logger = logging.getLogger("Professor")

    def analyze(self, symbol):
        """Ma'lum bir juftlikni analiz qilish"""
        self.logger.info(f"🔍 {symbol} tahlil qilinmoqda...")

        # Sham ma'lumotlarini olish (15m va 1h)
        df_15m = self.binance.fetch_ohlcv(symbol, '15m', 100)
        if df_15m is None or df_15m.empty:
            return None

        # TQI va SATS hisoblash
        tqi = calculate_tqi(df_15m).iloc[-1]
        upper, lower = calculate_sats_bands(df_15m, tqi)

        # SMC va ICT signallari
        smc_signals = detect_smc_ict(df_15m)

        # Oltin (PAXG) uchun vaqt filtri
        if symbol == config.GOLD_SYMBOL:
            # Bugun Shanba yoki Yakshanba ekanligini tekshirish (Python'da 5=Sat, 6=Sun)
            import datetime
            weekday = datetime.datetime.now().weekday()
            if weekday >= 5:
                self.logger.info(f"⌛ {symbol}: Dam olish kuni. Faqat setup yig'ilmoqda.")
                return {"signal": "SETUP", "tqi": tqi, "smc": smc_signals}

        # Signal mantiqi
        price = df_15m['close'].iloc[-1]

        # BUY Signal: TQI yuqori + SMC Bullish + Narx lower band'dan yuqoriga qaytsa
        if tqi > 0.4 and smc_signals['fvg_bull'] and price > lower.iloc[-1]:
            return {"signal": "BUY", "price": price, "tqi": tqi, "smc": smc_signals}

        # SELL Signal: TQI yuqori + SMC Bearish + Narx upper band'dan pastga qaytsa
        if tqi > 0.4 and smc_signals['fvg_bear'] and price < upper.iloc[-1]:
            return {"signal": "SELL", "price": price, "tqi": tqi, "smc": smc_signals}

        return {"signal": "WAIT", "tqi": tqi, "smc": smc_signals}
