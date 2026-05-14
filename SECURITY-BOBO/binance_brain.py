import time
import logging
import config
from binance_api import BinanceClient
from database import Database
from professor import Professor
from titan import Titan
from mergan import Mergan
from boss import Boss
from nazoratchi import Nazoratchi

# SECURITY-BOBO Asosiy Boshqaruv Markazi (Binance Brain)
# Barcha agentlarni swarm sifatida birlashtiradi

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("security_bobo.log"),
        logging.StreamHandler()
    ]
)

class BinanceBrain:
    def __init__(self):
        self.logger = logging.getLogger("BinanceBrain")
        self.logger.info(config.STATUS_MESSAGES["START"])

        # Modullarni yuklash
        self.binance = BinanceClient()
        self.db = Database()

        # Agentlarni yuklash
        self.professor = Professor(self.binance)
        self.titan = Titan(self.binance, self.db)
        self.mergan = Mergan(self.binance, self.db)
        self.boss = Boss(self.binance, self.db)
        self.nazoratchi = Nazoratchi(self.professor, self.titan)

        # Auto-Resume: Ochiq pozitsiyalarni tiklash
        self.boss.auto_resume()

    def run(self):
        """Asosiy tsikl"""
        while True:
            try:
                for symbol in config.SYMBOLS:
                    # 1. PROFESSOR tahlil qiladi
                    analysis = self.professor.analyze(symbol)

                    if analysis and analysis['signal'] in ["BUY", "SELL"]:
                        side = analysis['signal']
                        self.logger.info(f"🎯 Signal aniqlandi: {symbol} -> {side}")

                        # 2. TITAN riskni tekshiradi va lot hajmini hisoblaydi
                        amount = self.titan.calculate_position_size(symbol, analysis)

                        if self.titan.validate_trade(symbol, side, amount):
                            # 3. MERGAN savdoni ijro etadi
                            self.mergan.execute_trade(symbol, side, amount, analysis)

                # 4. BOSS ochiq pozitsiyalarni nazorat qiladi
                self.boss.monitor_positions()

                # 5. NAZORATCHI evolyutsiya o'tkazadi
                self.nazoratchi.evolve()

                # Kutish (Binance API rate limitlariga rioya qilish)
                time.sleep(10)

            except Exception as e:
                self.logger.error(config.STATUS_MESSAGES["ERROR"] + str(e))
                time.sleep(30)

if __name__ == "__main__":
    brain = BinanceBrain()
    brain.run()
