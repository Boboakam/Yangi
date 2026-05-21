import time
import logging
import threading
from binance_api import BinanceClient
from database import Database
from professor import Professor
from titan import Titan
from mergan import Mergan
from boss import Boss
from nazoratchi import Nazoratchi
import config

# Global Brain Instance for API access
brain_instance = None

class BinanceBrain:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("Brain")
        self.binance = BinanceClient()
        self.db = Database(config.DB_PATH)
        self.professor = Professor(self.binance)
        self.titan = Titan(self.binance, self.db)
        self.mergan = Mergan(self.binance, self.db)
        self.boss = Boss(self.binance, self.db)
        self.nazoratchi = Nazoratchi(self.professor, self.titan, self.boss, self.db)
        self.is_running = True

    def run(self):
        self.logger.info(config.STATUS_MESSAGES["START"])
        self.boss.auto_resume()

        while self.is_running:
            try:
                self.boss.monitor_positions()
                self.nazoratchi.check_heartbeat()

                for symbol in config.SYMBOLS:
                    analysis = self.professor.analyze(symbol)
                    if analysis and analysis['signal'] in ['BUY', 'SELL']:
                        if self.titan.validate_trade(symbol, analysis):
                            if self.nazoratchi.verify_absolute_facts(symbol, analysis['signal'], analysis['price']):
                                amount = self.titan.calculate_position_size(symbol, analysis)
                                if amount > 0:
                                    self.mergan.execute_trade(symbol, analysis['signal'], amount, analysis)

                self.nazoratchi.evolve_logic()
                time.sleep(10) # Optimallashtirilgan tezlik
            except Exception as e:
                self.logger.error(f"Brain Loop Error: {e}")
                time.sleep(30)

    def stop_and_panic(self):
        self.logger.warning("🆘 Brain: Panic Signal received!")
        self.is_running = False
        self.boss.close_all_on_emergency()

if __name__ == "__main__":
    brain = BinanceBrain()
    brain_instance = brain
    brain.run()
