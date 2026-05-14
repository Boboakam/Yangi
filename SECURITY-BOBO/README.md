# 🤖 SECURITY-BOBO v5.0 GODMODE

Ushbu tizim **Binance USDT-M Futures** tarmog'ida avtomatlashtirilgan savdo qilish uchun mo'ljallangan 5-Agentli (Swarm) mega tizimdir.

## 🌟 Asosiy Xususiyatlar
- **5-Agent Arxitekturasi:** Professor, Titan, Mergan, Boss va Nazoratchi.
- **Strategiya:** SMC, ICT, SATS va TQI algoritmlarining Python'dagi mukammal kombinatsiyasi.
- **Auto-Resume:** Internet yoki elektr uzilsa, tizim qayta ishga tushganda ochiq pozitsiyalarni darhol tanib oladi.
- **Touch-First Dashboard:** Planshet va sensorli noutbuklar uchun mo'ljallangan zamonaviy interfeys.
- **Telegram Notifier:** Barcha savdolar haqida real vaqtda O'zbek tilida xabarnomalar.

## 📂 Fayl Strukturasi (17 ta fayl)
1. `binance_brain.py` - Tizim markazi.
2. `professor.py` - Analiz agenti.
3. `titan.py` - Risk boshqaruvchisi.
4. `mergan.py` - Ijro etuvchi agent.
5. `boss.py` - Monitoring va tiklanish.
6. `nazoratchi.py` - Evolyutsiya markazi.
7. `indicators.py` - TQI/SATS/SMC algoritmlari.
8. `binance_api.py` - Binance API (ccxt).
9. `telegram_bot.py` - Telegram xabarnomalar.
10. `database.py` - SQLite bazasi.
11. `config.py` - Sozlamalar.
12. `utils.py` - Yordamchi funksiyalar.
13. `dashboard_server.py` - Backend API.
14. `frontend/Dashboard.jsx` - UI kodi.
15. `requirements.txt` - Kutubxonalar.
16. `test_system.py` - Testlar.
17. `README.md` - Ushbu qo'llanma.

## 🚀 Ishga tushirish
1. `requirements.txt` orqali kerakli kutubxonalarni yuklang: `pip install -r requirements.txt`
2. `config.py` fayliga Binance API va Telegram tokenlaringizni kiriting.
3. Tizimni ishga tushiring: `python binance_brain.py`
4. Dashboardni ko'rish uchun: `python dashboard_server.py` va brauzerda `localhost:8000` ga kiring.

## ⚠️ Ogohlantirish
Ushbu tizim agressiv savdo strategiyasidan foydalanadi. Savdo qilishdan oldin har doim test rejimida sinab ko'ring.

**Muallif:** BOBO AKAM
**Versiya:** 5.0.0 GODMODE
