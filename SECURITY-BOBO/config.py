# SECURITY-BOBO Konfiguratsiya fayli
# Barcha 30 ta evolyutsion qoida uchun markaziy sozlamalar

import os

# 1. BINANCE API SOZLAMALARI
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "Sizning_Binance_API_Key")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "Sizning_Binance_Secret_Key")

# 2. TELEGRAM BOT SOZLAMALARI
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "Sizning_Telegram_Bot_Token")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "Sizning_Chat_ID")

# 3. SAVDO JUFTLIKLARI VA BOZORLAR
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT"]
GOLD_SYMBOL = "PAXGUSDT"
BTC_SYMBOL = "BTCUSDT"

# 4. TITAN: RISK VA KAPITAL BOSHQARUVI (Rules 7-12)
INITIAL_CAPITAL = 25.0       # Boshlang'ich kapital (Safe-Lock uchun)
SAFE_LOCK_THRESHOLD = 50.0   # 50$ ga yetganda 25$ ni qulflash
RISK_PER_TRADE = 0.01        # Har bir savdo uchun 1% risk
MAX_DAILY_LOSS_PCT = 0.05    # Kunlik maksimal zarar 5%
CONSECUTIVE_LOSS_LIMIT = 3   # Qatorasiga 3 ta zarar
SLEEP_MODE_DURATION = 12     # Majburiy uyqu (soat)
LEVERAGE = 10                # Standart yelka

# 5. MERGAN: IJRO VA SEANSIYALAR (Rules 13-18)
# Nyu-York va London sessiyalari (UTC bo'yicha)
SESSION_KILLZONES = {
    "LONDON": {"start": 7, "end": 10},  # 07:00 - 10:00 UTC
    "NEW_YORK": {"start": 12, "end": 15} # 12:00 - 15:00 UTC
}
USE_LIMIT_ORDERS = True      # Doim Maker bo'lib kirish (Fee Optimizer)

# 6. PROFESSOR: TAHLIL VA FILTRLAR (Rules 1-6)
NEWS_FILTER_WINDOW = 30      # Yangilikdan 30 daqiqa oldin/keyin (minut)
MIN_TQI_SCORE = 0.6          # Kirish uchun minimal TQI balli
MTF_TIMEFRAMES = ["4h", "1h", "15m"]

# 7. BOSS: POZITSIYA BOSHQARUVI (Rules 19-24)
TIME_DECAY_EXIT_HOURS = 3    # 3 soat ichida foyda bo'lmasa yopish
ATR_TRAILING_MULT = 2.0      # Volatility Trailing koeffitsienti
SCALE_OUT_PERCENTS = [0.25, 0.50] # Qismlab foyda olish (25%, 50%)

# 8. NAZORATCHI: XAVFSIZLIK VA EVOLYUTSIYA (Rules 25-30)
HEARTBEAT_INTERVAL = 6       # 6 soatda bir hisobot (soat)
GHOST_MODE = False           # Paper Trading holati
MARKET_REGIMES = ["TREND", "CHOPPY", "ACCUMULATION", "DISTRIBUTION"]

# 9. TIZIM INFRATUZILMASI
DB_PATH = "security_bobo.db"
DASHBOARD_PORT = 8000
DASHBOARD_HOST = "0.0.0.0"

# O'ZBEKCHA STATUS XABARLARI
STATUS_MESSAGES = {
    "START": "🚀 SECURITY-BOBO A1: Tizim muvaffaqiyatli ishga tushdi!",
    "STOP": "🛑 Tizim to'xtatildi.",
    "SLEEP": "😴 Tizim 'Sleep Mode' holatiga o'tdi (3 ta zarar sababli).",
    "PANIC": "🆘 EMERGENCY: Barcha pozitsiyalar yopildi!",
    "HEARTBEAT": "💓 Heartbeat: Tizim barqaror ishlamoqda.",
    "AUTO_RESUME": "🔄 Auto-Resume: Ochiq pozitsiyalar nazoratga olindi."
}
