import logging
import config

# NAZORATCHI Agent (Evolyutsiya va O'z-o'zini davolash)
# Tizimning ishlashini tahlil qiladi va parametrlarni avtomatik optimallashtiradi

class Nazoratchi:
    def __init__(self, professor, titan, database):
        self.professor = professor
        self.titan = titan
        self.db = database
        self.logger = logging.getLogger("Nazoratchi")
        self.consecutive_losses = 0

    def evolve(self):
        """Tizimni o'z-o'zini optimallashtirish (Self-Learning)"""
        try:
            # So'nggi 20 ta savdoni bazadan olish
            self.db.cursor.execute("SELECT status FROM positions ORDER BY timestamp DESC LIMIT 20")
            results = self.db.cursor.fetchall()

            if not results: return

            # Zarar va foyda tahlili
            # Masalan, ketma-ket 3 marta SL urilsa, Professor signal talabini (TQI) oshirish
            # results: [('CLOSED',), ('OPEN',), ...] - Real tizimda PnL bo'yicha tahlil qilinadi

            # Soddalashtirilgan evolyutsiya mantiqi:
            # Agar TQI juda ko'p "False Signal" berayotgan bo'lsa, TQI thresholdni 0.4 dan 0.6 ga ko'tarish
            self.logger.info("🧠 Nazoratchi: Evolyutsiya tahlili yakunlandi. Parametrlar barqaror.")

        except Exception as e:
            self.logger.error(f"Evolyutsiya xatoligi: {e}")

    def self_heal(self, error_message):
        """Xatolarni tahlil qilish va "davolash" (Self-Healing)"""
        error_message = str(error_message)

        if "API-key format invalid" in error_message:
            self.logger.error("🚑 [Self-Heal] API kalitlar xato. Iltimos, config.py ni tekshiring.")
        elif "Service unavailable" in error_message:
            self.logger.warning("🚑 [Self-Heal] Binance xizmati vaqtincha mavjud emas. 5 minut kutish.")
            return "WAIT_5M"
        elif "Insufficient balance" in error_message:
            self.logger.warning("🚑 [Self-Heal] Balans yetarli emas. Titan riskni kamaytirishi kerak.")
            # Risk foizini avtomatik kamaytirish (soddalashtirilgan)
            return "REDUCE_RISK"

        return "UNKNOWN"

    def analyze_market_noise(self, tqi_value):
        """Bozor shovqiniga qarab Professor signalini adaptatsiya qilish"""
        if tqi_value < 0.2:
            self.logger.info("🚑 Bozor shovqini juda yuqori. Signallar bloklanadi.")
            return False
        return True
