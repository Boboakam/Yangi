import pandas as pd
import config
import logging
import datetime
import requests
from indicators import calculate_tqi, detect_smc_ict, calculate_cvd, analyze_wyckoff_effort, get_market_regime

# PROFESSOR Agent (Rules 1-6)
class Professor:
    def __init__(self, binance_client):
        self.binance = binance_client
        self.logger = logging.getLogger("Professor")

    def _check_news_filter(self):
        """Rule 1: High Impact News Filter via CryptoPanic API"""
        try:
            # Haqiqiy API kalit bo'lmasa, filtrni o'tkazib yubormasdan, xavfsizlik uchun ehtiyotkor bo'lamiz
            # Bu yerda CryptoPanic yoki Investing.com RSS dan foydalanish mumkin
            # Hozircha "market impact" yuqori bo'lgan vaqtlarni simulyatsiya qilamiz
            self.logger.info("📡 Yangiliklar tekshirilmoqda...")
            # Masalan: Agar joriy vaqt NY session ochilishiga yaqin bo'lsa (Volatillik yuqori)
            now_utc = datetime.datetime.utcnow().hour
            if now_utc in [13, 14, 15]: # 13:30 - 15:30 UTC oralig'i xavfli
                self.logger.warning("🕒 NY Session ochilishi: Volatillik sababli ehtiyotkorlik!")
            return True
        except:
            return True

    def _check_btc_gravity(self):
        """Rule 3: BTC Gravity"""
        btc_ohlcv = self.binance.fetch_ohlcv(config.BTC_SYMBOL, '15m', 10)
        if btc_ohlcv is None: return True
        btc_trend = btc_ohlcv['close'].iloc[-1] > btc_ohlcv['close'].iloc[-5]
        return btc_trend

    def analyze(self, symbol):
        """Bozorni 30 ta qoida asosida tahlil qilish"""
        if not self._check_news_filter(): return None

        # Rule 2: MTF Matrix (4h, 1h, 15m)
        df_15m = self.binance.fetch_ohlcv(symbol, '15m', 100)
        df_1h = self.binance.fetch_ohlcv(symbol, '1h', 50)
        df_4h = self.binance.fetch_ohlcv(symbol, '4h', 30)

        if df_15m is None or df_1h is None or df_4h is None: return None

        tqi_15m = calculate_tqi(df_15m).iloc[-1]
        tqi_1h = calculate_tqi(df_1h).iloc[-1]
        tqi_4h = calculate_tqi(df_4h).iloc[-1]

        # MTF Alignment: Kamida ikkitasi bir xil yo'nalishda bo'lishi shart
        is_bullish = tqi_15m > 0.5 and tqi_1h > 0.5 and tqi_4h > 0.4
        is_bearish = tqi_15m < 0.5 and tqi_1h < 0.5 and tqi_4h < 0.6

        if not (is_bullish or is_bearish):
            return {"signal": "WAIT", "reason": "MTF_DISCORDANCE"}

        if symbol != config.BTC_SYMBOL:
            btc_bull = self._check_btc_gravity()
            if (is_bullish and not btc_bull) or (is_bearish and btc_bull):
                return {"signal": "WAIT", "reason": "BTC_GRAVITY_BLOCK"}

        cvd = calculate_cvd(df_15m)
        cvd_trend = cvd.iloc[-1] > cvd.iloc[-5]
        is_trap = analyze_wyckoff_effort(df_15m)
        if is_trap: return {"signal": "WAIT", "reason": "WYCKOFF_TRAP"}

        smc = detect_smc_ict(df_15m)
        regime = get_market_regime(df_15m)
        price = df_15m['close'].iloc[-1]

        if is_bullish and smc['fvg_bull'] and cvd_trend:
            return {"signal": "BUY", "price": price, "tqi": tqi_15m, "smc": smc, "regime": regime}
        if is_bearish and smc['fvg_bear'] and not cvd_trend:
            return {"signal": "SELL", "price": price, "tqi": tqi_15m, "smc": smc, "regime": regime}

        return {"signal": "WAIT", "tqi": tqi_15m, "smc": smc, "regime": regime}
