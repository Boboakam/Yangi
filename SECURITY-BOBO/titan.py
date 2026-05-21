import config
import logging
import datetime

# TITAN Agent (Rules 7-12)
# Risk, Kapital Himoyasi va Safe-Lock bo'yicha mas'ul

class Titan:
    def __init__(self, binance_client, database):
        self.binance = binance_client
        self.db = database
        self.logger = logging.getLogger("Titan")
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.date.today()
        self.consecutive_losses = 0
        self.sleep_mode_until = None
        self.virtual_pool = 0.0 # Rule 12

    def _check_sleep_mode(self):
        """Rule 9: Consecutive Loss Breaker"""
        if self.sleep_mode_until and datetime.datetime.now() < self.sleep_mode_until:
            return True
        return False

    def calculate_position_size(self, symbol, signal_info):
        """Rule 7 & 10: Safe-Lock va Drawdown Morphing"""
        balance = self.binance.get_balance()
        if balance <= 0: return 0

        # Rule 7: Safe-Lock ($25 ni qulflash)
        available_balance = balance
        if balance >= config.SAFE_LOCK_THRESHOLD:
            available_balance = balance - config.INITIAL_CAPITAL
            self.logger.info(f"🔒 Safe-Lock: {config.INITIAL_CAPITAL}$ qulflangan.")

        # Rule 10: Drawdown Morphing
        risk_pct = config.RISK_PER_TRADE
        if self.daily_pnl < 0:
            reduction = min(abs(self.daily_pnl) / balance * 5, 0.8) # Maksimal 80% qisqartirish
            risk_pct = risk_pct * (1 - reduction)

        risk_amount = available_balance * risk_pct
        price = signal_info['price']

        # Rule 11: Asymmetric Payoff (1:2 - 1:5)
        # Soddalashtirilgan: miqdor hisoblashda leverage ishlatiladi
        amount = (risk_amount * config.LEVERAGE) / price

        # Precision
        if "BTC" in symbol: amount = round(amount, 3)
        elif "ETH" in symbol: amount = round(amount, 2)
        else: amount = round(amount, 1)

        return amount

    def validate_trade(self, symbol, signal_info):
        """Rule 8 & 9: Safety Limits"""
        if self._check_sleep_mode(): return False

        # Rule 8: Funding Rate Radar
        funding_rate = self.binance.get_funding_rate(symbol)
        side = signal_info['signal']
        if (side == "BUY" and funding_rate > 0.001) or (side == "SELL" and funding_rate < -0.001):
            return False

        return True

    def record_trade_result(self, pnl):
        """Rule 12: Capital Evolution Pool"""
        self.daily_pnl += pnl
        if pnl > 0:
            # Foydaning 20% qismini virtual hovuzga o'tkazish
            contribution = pnl * 0.2
            self.virtual_pool += contribution
            self.logger.info(f"💰 Capital Pool Evolution: +{contribution} USDT")

        if pnl < 0:
            self.consecutive_losses += 1
            if self.consecutive_losses >= config.CONSECUTIVE_LOSS_LIMIT:
                self.sleep_mode_until = datetime.datetime.now() + datetime.timedelta(hours=config.SLEEP_MODE_DURATION)
        else:
            self.consecutive_losses = 0

    def get_capital_evolution(self):
        """Rule 12: Hovuz holati"""
        return self.virtual_pool
