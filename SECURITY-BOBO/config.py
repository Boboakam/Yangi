# SECURITY-BOBO Konfiguratsiya fayli
# Barcha sozlamalar shu yerda saqlanadi

import os

# Binance API Sozlamalari (Foydalanuvchi o'z kalitlarini kiritishi kerak)
BINANCE_API_KEY = "Sizning_Binance_API_Key"
BINANCE_SECRET_KEY = "Sizning_Binance_Secret_Key"

# Telegram Bot Sozlamalari
TELEGRAM_BOT_TOKEN = "Sizning_Telegram_Bot_Token"
TELEGRAM_CHAT_ID = "Sizning_Chat_ID"

# Savdo Juftliklari
# Oltin uchun PAXGUSDT ishlatiladi (Binance Futures'da eng yaqini)
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PAXGUSDT"]
GOLD_SYMBOL = "PAXGUSDT"

# Risk Sozlamalari (TITAN uchun)
RISK_PER_TRADE = 0.01  # Balansning 1% i har bir savdo uchun
MAX_DAILY_LOSS = 0.05   # Kunlik maksimal zarar 5%
MAX_DRAWDOWN = 0.15     # Maksimal Drawdown 15%
LEVERAGE = 10           # Yelka (Leverage)

# TQI va SATS Sozlamalari (PROFESSOR uchun)
ATR_LENGTH = 13
BASE_MULTIPLIER = 2.0
ER_LENGTH = 20
STRUCTURE_WINDOW = 20

# Ma'lumotlar bazasi
DB_PATH = "security_bobo.db"

# Dashboard sozlamalari
DASHBOARD_PORT = 8000
DASHBOARD_HOST = "0.0.0.0"

# O'zbekcha status xabarlari
STATUS_MESSAGES = {
    "START": "🚀 SECURITY-BOBO Tizimi ishga tushdi!",
    "STOP": "🛑 Tizim to'xtatildi.",
    "ERROR": "❌ Xatolik yuz berdi: ",
    "TRADE_OPEN": "🟢 Yangi pozitsiya ochildi: ",
    "TRADE_CLOSE": "🔴 Pozitsiya yopildi: ",
    "RECOVERY": "🔄 Auto-Resume: Ochiq pozitsiyalar qayta tiklandi."
}
