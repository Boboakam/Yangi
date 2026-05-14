import ccxt
import config
import logging
import pandas as pd

# Binance API bilan aloqa moduli
# ccxt kutubxonasi orqali Futures savdosi amalga oshiriladi

class BinanceClient:
    def __init__(self):
        self.client = ccxt.binance({
            'apiKey': config.BINANCE_API_KEY,
            'secret': config.BINANCE_SECRET_KEY,
            'options': {'defaultType': 'future'},
            'enableRateLimit': True
        })
        self.logger = logging.getLogger("BinanceAPI")

    def fetch_ohlcv(self, symbol, timeframe='15m', limit=100):
        """Sham ma'lumotlarini olish va DataFrame ga o'tkazish"""
        try:
            ohlcv = self.client.fetch_ohlcv(symbol, timeframe, limit=limit)
            if not ohlcv:
                return None
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            # Vaqtni o'qiladigan formatga o'tkazish
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            self.logger.error(f"OHLCV olishda xatolik: {e}")
            return None

    def get_balance(self):
        """USDT balansini olish"""
        try:
            balance = self.client.fetch_balance()
            return balance['total'].get('USDT', 0)
        except Exception as e:
            self.logger.error(f"Balans olishda xatolik: {e}")
            return 0

    def open_order(self, symbol, side, amount, params={}):
        """Order ochish"""
        try:
            # Miqdorni aniqlashtirish (Precision)
            order = self.client.create_order(symbol, 'market', side, amount, params=params)
            return order
        except Exception as e:
            self.logger.error(f"Order ochishda xatolik: {e}")
            return None

    def get_open_positions(self, symbol=None):
        """Ochiq pozitsiyalarni olish"""
        try:
            positions = self.client.fetch_positions(symbols=[symbol] if symbol else None)
            # Faqat ochiq (miqdori 0 dan katta) pozitsiyalarni qaytarish
            active_positions = []
            for p in positions:
                if float(p.get('contracts', 0)) > 0:
                    active_positions.append(p)
            return active_positions
        except Exception as e:
            self.logger.error(f"Pozitsiyalarni olishda xatolik: {e}")
            return []

    def set_leverage(self, symbol, leverage):
        """Yelkani sozlash"""
        try:
            # Symbol formatini Binance API ga moslash (masalan BTC/USDT -> BTCUSDT)
            clean_symbol = symbol.replace("/", "")
            self.client.fapiPrivate_post_leverage({
                "symbol": clean_symbol,
                "leverage": int(leverage)
            })
        except Exception as e:
            self.logger.error(f"Leverage sozlashda xatolik: {e}")

    def get_ticker(self, symbol):
        """Joriy narxni olish"""
        try:
            ticker = self.client.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            self.logger.error(f"Ticker olishda xatolik: {e}")
            return None
