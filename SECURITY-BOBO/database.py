import sqlite3
import config
import logging

# SQLite Ma'lumotlar bazasi moduli
# Auto-Resume va savdo tarixini saqlash uchun ishlatiladi

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.logger = logging.getLogger("Database")

    def create_tables(self):
        """Jadvallarni yaratish"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                side TEXT,
                amount REAL,
                entry_price REAL,
                sl REAL,
                tp REAL,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_profit REAL,
                daily_pnl REAL,
                win_rate REAL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_position(self, symbol, side, amount, entry_price, sl, tp):
        """Yangi pozitsiyani saqlash"""
        try:
            self.cursor.execute('''
                INSERT INTO positions (symbol, side, amount, entry_price, sl, tp, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, side, amount, entry_price, sl, tp, 'OPEN'))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Pozitsiyani saqlashda xatolik: {e}")

    def get_open_positions(self):
        """Ochiq pozitsiyalarni bazadan olish"""
        self.cursor.execute("SELECT * FROM positions WHERE status = 'OPEN'")
        return self.cursor.fetchall()

    def close_position(self, symbol):
        """Pozitsiyani yopilgan deb belgilash"""
        self.cursor.execute("UPDATE positions SET status = 'CLOSED' WHERE symbol = ? AND status = 'OPEN'", (symbol,))
        self.conn.commit()

    def clear_all(self):
        """Barcha ma'lumotlarni tozalash (test uchun)"""
        self.cursor.execute("DELETE FROM positions")
        self.conn.commit()
