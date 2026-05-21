import ccxt
import config
import logging
import pandas as pd

# SECURITY-BOBO Binance API Interfeysi
# Funding Rate, Order Book va Likvidatsiyalarni qo'llab-quvvatlaydi

class BinanceClient:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': config.BINANCE_API_KEY,
            'secret': config.BINANCE_SECRET_KEY,
            'options': {'defaultType': 'future'},
            'enableRateLimit': True
        })
        self.logger = logging.getLogger("BinanceClient")

    def fetch_ohlcv(self, symbol, timeframe='15m', limit=100):
        """Sham ma'lumotlarini olish"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            self.logger.error(f"OHLCV olishda xatolik ({symbol}): {e}")
            return None

    def get_balance(self):
        """USDT balansini olish"""
        try:
            balance = self.exchange.fetch_balance()
            return float(balance['total']['USDT'])
        except:
            return 0.0

    def get_funding_rate(self, symbol):
        """Binance Funding Rate Radar (Rule 8)"""
        try:
            funding = self.exchange.fetch_funding_rate(symbol)
            return funding['fundingRate']
        except:
            return 0.0

    def get_order_book(self, symbol, limit=20):
        """Order Book ma'lumotlari (Spoofing Guard uchun)"""
        try:
            return self.exchange.fetch_order_book(symbol, limit)
        except:
            return None

    def get_open_positions(self):
        """Barcha ochiq pozitsiyalarni olish (Auto-Resume uchun)"""
        try:
            positions = self.exchange.fetch_positions()
            return [p for p in positions if float(p['contracts']) > 0]
        except:
            return []

    def open_order(self, symbol, side, amount, params={}):
        """Buyruq yuborish (Rule 13: Maker/Limit optimizatsiyasi)"""
        try:
            # Agar limit order bo'lsa, joriy narxdan biroz yaxshiroq narx qo'yish
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['ask'] if side == 'buy' else ticker['bid']

            order = self.exchange.create_order(
                symbol=symbol,
                type='limit' if config.USE_LIMIT_ORDERS else 'market',
                side=side,
                amount=amount,
                price=price if config.USE_LIMIT_ORDERS else None,
                params=params
            )
            return order
        except Exception as e:
            self.logger.error(f"Order yuborishda xatolik: {e}")
            return None

    def set_leverage(self, symbol, leverage):
        """Yelkani sozlash"""
        try:
            self.exchange.set_leverage(leverage, symbol)
        except:
            pass

    def get_ticker(self, symbol):
        """Joriy narxni olish"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except:
            return None
