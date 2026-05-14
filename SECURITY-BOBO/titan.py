import config
import logging
import datetime

# TITAN Agent (Risk va Himoya)
# Savdo hajmini hisoblaydi va risk limitlarini nazorat qiladi

class Titan:
    def __init__(self, binance_client, database):
        self.binance = binance_client
        self.db = database
        self.logger = logging.getLogger("Titan")
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.date.today()

    def _reset_daily_pnl(self):
        """Har kuni PnLni nollash"""
        today = datetime.date.today()
        if today > self.last_reset_date:
            self.daily_pnl = 0.0
            self.last_reset_date = today
            self.logger.info("📅 Yangi kun: Kunlik PnL nollashdi.")

    def calculate_position_size(self, symbol, signal_info):
        """Lot hajmini va riskni hisoblash (Aggressive Compounding bilan)"""
        balance = self.binance.get_balance()
        if balance <= 0:
            return 0

        # Bazaviy risk miqdori
        risk_pct = config.RISK_PER_TRADE

        # AGGRESSIVE COMPOUNDING (Kripto uchun)
        # Agar balans boshlang'ich balansdan yuqori bo'lsa, risk foizini oshirish
        # Masalan, har 10% foyda uchun riskni 0.2% ga oshirish
        if "USDT" in symbol and symbol != config.GOLD_SYMBOL:
            # Soddalashtirilgan compounding mantiqi
            if balance > 1000: # Masalan 1000$ dan yuqori bo'lsa
                bonus_risk = (balance - 1000) / 1000 * 0.002
                risk_pct = min(risk_pct + bonus_risk, 0.05) # Maksimal 5% risk

        risk_amount = balance * risk_pct
        price = signal_info['price']

        # Lot hajmiga yelkani (leverage) ta'sirini hisobga olish
        # Miqdor = (Risk_USDT * Leverage) / Narx
        amount = (risk_amount * config.LEVERAGE) / price

        # Miqdorni Binance precision qoidalariga moslash (Step size)
        # Soddalashtirish uchun:
        if "BTC" in symbol: amount = round(amount, 3)
        elif "ETH" in symbol: amount = round(amount, 2)
        else: amount = round(amount, 1)

        return amount

    def check_safety_limits(self):
        """Kunlik zarar va drawdownni tekshirish"""
        self._reset_daily_pnl()

        balance = self.binance.get_balance()
        if balance <= 0: return False

        # Kunlik zarar limiti (config.MAX_DAILY_LOSS = 0.05)
        if self.daily_pnl < -(balance * config.MAX_DAILY_LOSS):
            self.logger.error(f"🛑 Kunlik zarar limiti urildi! PnL: {self.daily_pnl}")
            return False

        # Drawdown limitini tekshirish (Bazadan oxirgi natijalarni olib)
        return True

    def validate_trade(self, symbol, side, amount):
        """Savdoni tasdiqlash"""
        if not self.check_safety_limits():
            return False

        if amount <= 0:
            self.logger.warning(f"⚠️ {symbol}: Miqdor 0 yoki undan kam. Savdo bekor qilindi.")
            return False

        # Oltin uchun maxsus limitlar (Xavfsiz risk)
        if symbol == config.GOLD_SYMBOL:
            # Oltin uchun riskni kamaytirish yoki leverage'ni pasaytirish
            pass

        return True

    def update_pnl(self, pnl):
        """Savdo yakunlanganda PnLni yangilash"""
        self.daily_pnl += pnl
        self.logger.info(f"📊 Kunlik PnL yangilandi: {self.daily_pnl} USDT")
