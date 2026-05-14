import time
import datetime
import logging
import os

# SECURITY-BOBO Yordamchi Funksiyalar Moduli

def get_timestamp():
    """Joriy vaqtni o'qiladigan formatda olish"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_number(val, precision=2):
    """Sonlarni formatlash"""
    try:
        return f"{float(val):.{precision}f}"
    except:
        return str(val)

def check_file_exists(filepath):
    """Fayl mavjudligini tekshirish"""
    return os.path.exists(filepath)

def setup_logger(name, log_file="security_bobo.log"):
    """Logger sozlash (Agentlar uchun)"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def is_market_open(symbol):
    """Bozor ochiqligini tekshirish (XAUUSDT uchun hafta oxiri filtri)"""
    if "PAXG" in symbol or "XAU" in symbol:
        weekday = datetime.datetime.now().weekday()
        if weekday >= 5: # Shanba va Yakshanba
            return False
    return True
