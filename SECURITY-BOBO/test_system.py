import unittest
import os
import config
from database import Database
from indicators import calculate_tqi
import pandas as pd
import numpy as np

class TestSecurityBobo(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_bobo.db"
        self.db = Database(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_database_save_and_get(self):
        """Ma'lumotlar bazasini tekshirish"""
        self.db.save_position("BTCUSDT", "BUY", 0.01, 50000, 49000, 55000)
        positions = self.db.get_open_positions()
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0][1], "BTCUSDT")

    def test_tqi_calculation(self):
        """TQI indikatorini tekshirish"""
        data = {
            'high': np.random.random(150) + 100,
            'low': np.random.random(150) + 98,
            'open': np.random.random(150) + 99,
            'close': np.random.random(150) + 99,
            'volume': np.random.random(150) * 1000
        }
        df = pd.DataFrame(data)
        tqi = calculate_tqi(df)
        self.assertEqual(len(tqi), 150)
        self.assertTrue(tqi.iloc[-1] >= 0)

if __name__ == '__main__':
    unittest.main()
