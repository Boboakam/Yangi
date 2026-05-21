# SECURITY-BOBO Utility Moduli
# Yordamchi funksiyalar va hisob-kitoblar

import datetime
import logging

def format_currency(value):
    """Valyutani chiroyli formatda ko'rsatish"""
    return f"{value:,.2f} USDT"

def get_timestamp():
    """Hozirgi vaqtni UTC formatda olish"""
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

def setup_logger(name):
    """Logerlarni sozlash"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def calculate_drawdown(peak, current):
    """Drawdownni hisoblash"""
    if peak <= 0: return 0.0
    return (peak - current) / peak
