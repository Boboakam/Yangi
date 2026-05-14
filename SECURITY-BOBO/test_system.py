import unittest
from indicators import calculate_atr, calculate_tqi
import pandas as pd
import numpy as np

class TestSecurityBobo(unittest.TestCase):
    def setUp(self):
        # Test uchun dummy ma'lumotlar
        data = {
            'high': np.random.random(100) + 100,
            'low': np.random.random(100) + 99,
            'close': np.random.random(100) + 99.5
        }
        self.df = pd.DataFrame(data)

    def test_indicators(self):
        """Indikatorlar to'g'ri hisoblanishini tekshirish"""
        atr = calculate_atr(self.df)
        self.assertEqual(len(atr), 100)

        tqi = calculate_tqi(self.df)
        self.assertEqual(len(tqi), 100)
        self.assertTrue(all(tqi >= 0) and all(tqi <= 1))

    def test_config(self):
        """Config faylini tekshirish"""
        import config
        self.assertEqual(config.GOLD_SYMBOL, "PAXGUSDT")
        self.assertIn("BTCUSDT", config.SYMBOLS)

if __name__ == "__main__":
    unittest.main()
