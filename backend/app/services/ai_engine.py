import os
from functools import lru_cache
from app.core.config import settings

class AIEngineService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        self.enabled = bool(self.api_key)
        self.model_name = "gemini-1.5-flash"
        self.client = None
        if self.enabled:
            # Imported lazily so the deprecated-free SDK is only loaded when a key is set
            from google import genai
            self.client = genai.Client(api_key=self.api_key)

    def generate_match_preview(self, home_team: str, away_team: str, league_name: str) -> str:
        prompt = f"""
        Siz sport tahlilchisisiz. Quyidagi futbol uchrashuvi uchun qisqa va qiziqarli o'yinoldi (match preview) tahlilini o'zbek tilida yozib bering.
        Liga: {league_name}
        Mezbon: {home_team}
        Mehmon: {away_team}
        
        Tahlil quyidagilarni o'z ichiga olsin:
        1. Har bir jamoaning ayni paytdagi holati haqida qisqacha.
        2. Uchrashuv qanchalik muhimligi.
        3. Taxminiy o'yin uslubi.
        Maksimal 3-4 ta xatboshi bo'lsin.
        """
        if self.enabled:
            try:
                response = self.client.models.generate_content(model=self.model_name, contents=prompt)
                return response.text.strip()
            except Exception as e:
                print(f"Gemini API Error in generate_match_preview: {e}")
        
        # Rule-based fallback (Uzbek templates)
        return (
            f"**{league_name}** doirasida kutilayotgan murosasiz to'qnashuv! **{home_team}** o'z maydonida **{away_team}** jamoasini qabul qiladi.\n\n"
            f"Mezbon jamoa so'nggi turlarda barqaror o'yin ko'rsatmoqda va turnir jadvalida yuqori o'rinlar uchun kurashmoqda. "
            f"Biroq, mehmon bo'lib kelayotgan **{away_team}** tarkib jihatidan ancha kuchli va har qanday raqibga jiddiy muammo tug'dira oladi.\n\n"
            f"Ekspertlarimiz fikriga ko'ra, o'yin asosan maydon markazidagi kurashlar va tezkor qarshi hujumlar ustiga quriladi. "
            f"O'z maydoni omili {home_team}ga qo'shimcha ishonch berishi aniq."
        )

    def generate_post_match_analysis(self, home_team: str, away_team: str, score: str, stats: dict, events: list) -> str:
        events_str = ", ".join([f"{e.get('time')}-daqiqa: {e.get('detail')}" for e in events]) if events else "Jiddiy voqealar yuz bermadi"
        prompt = f"""
        Siz professional futbol ekspertisiz. Tugagan o'yin bo'yicha tahliliy maqola yozib bering (o'zbek tilida).
        Uchrashuv: {home_team} {score} {away_team}
        Statistika: {stats}
        Asosiy voqealar: {events_str}
        
        Tahlilda o'yinning burilish nuqtalari, statistik ko'rsatkichlarning tahlili va g'alaba sabablarini yoritib bering.
        """
        if self.enabled:
            try:
                response = self.client.models.generate_content(model=self.model_name, contents=prompt)
                return response.text.strip()
            except Exception as e:
                print(f"Gemini API Error in generate_post_match_analysis: {e}")
                
        return (
            f"**{home_team} - {away_team} ({score}) o'yini yakunlandi.**\n\n"
            f"Uchrashuv kutilganidek shiddatli kechdi. Statistika tahliliga ko'ra, "
            f"to'p nazorati asosan maydondagi ustunlikni belgilab berdi. {home_team} jamoasi yaratilgan vaziyatlardan "
            f"yaxshiroq foydalangan holda g'alabani qo'lga kiritdi.\n\n"
            f"Uchrashuvning eng yorqin daqiqalari va muhim pallalari ushbu natijani aniqlab berdi. "
            f"Ikkala jamoa murabbiylari ham o'yindan so'ng taktik o'zgarishlar haqida to'xtalib o'tishlari kutilmoqda."
        )

    def generate_news_article(self, topic: str) -> dict:
        prompt = f"""
        Futbol olamidagi quyidagi mavzu bo'yicha qisqa, SEO-optimizatsiya qilingan sport yangiligi yozib bering (o'zbek tilida).
        Mavzu: {topic}
        
        Natija JSON formatida bo'lsin:
        {{
            "title": "SEO sarlavha",
            "summary": "Qisqa annotatsiya (1-2 gap)",
            "content": "To'liq maqola mazmuni (markdown formatida)",
            "tags": ["tag1", "tag2"]
        }}
        Faqat JSON qaytaring, boshqa hech qanday tekst bo'lmasin.
        """
        if self.enabled:
            try:
                import json
                response = self.client.models.generate_content(model=self.model_name, contents=prompt)
                clean_text = response.text.strip().replace("```json", "").replace("```", "")
                return json.loads(clean_text)
            except Exception as e:
                print(f"Gemini API Error in generate_news_article: {e}")
        
        # Rule-based fallback news
        slug_topic = topic.lower().replace(" ", "-")
        return {
            "title": f"Dahshatli Transfer: {topic} bo'yicha yangi tafsilotlar",
            "summary": f"Yevropa futbolida yangi mish-mishlar va rasmiy muzokaralar qizg'in pallaga kirdi. Batafsil bizning maqolamizda.",
            "content": (
                f"### Transfer Bozoridagi So'nggi Yangiliklar\n\n"
                f"Futbol olamida katta shov-shuvlarga sabab bo'layotgan **{topic}** masalasi kun tartibidagi eng muhim mavzu bo'lib turibdi.\n\n"
                f"Nufuzli insayderlarning xabar berishicha, jamoalar kelishuv shartlarini kelishib olishgan va yaqin kunlarda tibbiy ko'riklar rejalashtirilgan. "
                f"Muxlislar ushbu kelishuvning yakunlanishini sabrsizlik bilan kutishmoqda.\n\n"
                f"Batafsil yangiliklarni AI Football Hub Uzbekistan platformasida kuzatib boring!"
            ),
            "tags": ["transfer", "futbol", "breaking", slug_topic]
        }


@lru_cache
def get_ai_engine() -> AIEngineService:
    """FastAPI dependency: returns a single shared AIEngineService instance."""
    return AIEngineService()
