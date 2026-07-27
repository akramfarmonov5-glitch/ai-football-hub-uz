import asyncio
import json
import logging
import os
from functools import lru_cache
from typing import Any, Dict, List

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIEngineService:
    """Gemini orqali matn generatsiyasi; kalit bo'lmasa shablonli matn qaytaradi.

    Muhim: Gemini SDK sinxron ishlaydi. Uni to'g'ridan-to'g'ri async endpointda
    chaqirish butun event loop'ni bloklaydi — ya'ni AI javobini kutayotgan
    10 soniyada API ham, jonli WebSocket yangilanishlari ham to'xtab qoladi.
    Shuning uchun har bir chaqiruv `asyncio.to_thread` orqali alohida oqimda
    bajariladi.
    """

    def __init__(self) -> None:
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        self.enabled = bool(self.api_key)
        self.model_name = settings.GEMINI_MODEL
        self.client = None
        if self.enabled:
            # Kalit bo'lgandagina yuklaymiz — kalitsiz ishga tushishga xalaqit bermaydi
            from google import genai

            self.client = genai.Client(api_key=self.api_key)
            logger.info("AI dvigateli yoqildi (model: %s)", self.model_name)
        else:
            logger.info("GEMINI_API_KEY yo'q — shablonli matnlar ishlatiladi")

    # ------------------------------------------------------------------
    # Ichki yordamchi
    # ------------------------------------------------------------------
    async def _generate(self, prompt: str) -> str:
        """Gemini'ga so'rov yuboradi. Xato yoki kalit yo'q bo'lsa bo'sh satr."""
        if not self.enabled:
            return ""
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
            )
            return (response.text or "").strip()
        except Exception as exc:
            logger.warning("Gemini xatosi: %s", exc)
            return ""

    # ------------------------------------------------------------------
    # Ommaviy metodlar
    # ------------------------------------------------------------------
    async def generate_match_preview(
        self, home_team: str, away_team: str, league_name: str
    ) -> str:
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
        generated = await self._generate(prompt)
        if generated:
            return generated

        # Qoidaga asoslangan zaxira matn (o'zbekcha shablon)
        return (
            f"**{league_name}** doirasida kutilayotgan murosasiz to'qnashuv! **{home_team}** o'z maydonida **{away_team}** jamoasini qabul qiladi.\n\n"
            f"Mezbon jamoa so'nggi turlarda barqaror o'yin ko'rsatmoqda va turnir jadvalida yuqori o'rinlar uchun kurashmoqda. "
            f"Biroq, mehmon bo'lib kelayotgan **{away_team}** tarkib jihatidan ancha kuchli va har qanday raqibga jiddiy muammo tug'dira oladi.\n\n"
            f"Ekspertlarimiz fikriga ko'ra, o'yin asosan maydon markazidagi kurashlar va tezkor qarshi hujumlar ustiga quriladi. "
            f"O'z maydoni omili {home_team}ga qo'shimcha ishonch berishi aniq."
        )

    async def generate_post_match_analysis(
        self,
        home_team: str,
        away_team: str,
        score: str,
        stats: Dict[str, Any],
        events: List[Dict[str, Any]],
    ) -> str:
        events_str = (
            ", ".join(f"{e.get('time')}-daqiqa: {e.get('detail')}" for e in events)
            if events
            else "Jiddiy voqealar yuz bermadi"
        )
        prompt = f"""
        Siz professional futbol ekspertisiz. Tugagan o'yin bo'yicha tahliliy maqola yozib bering (o'zbek tilida).
        Uchrashuv: {home_team} {score} {away_team}
        Statistika: {stats}
        Asosiy voqealar: {events_str}

        Tahlilda o'yinning burilish nuqtalari, statistik ko'rsatkichlarning tahlili va g'alaba sabablarini yoritib bering.
        """
        generated = await self._generate(prompt)
        if generated:
            return generated

        return (
            f"**{home_team} - {away_team} ({score}) o'yini yakunlandi.**\n\n"
            f"Uchrashuv kutilganidek shiddatli kechdi. Statistika tahliliga ko'ra, "
            f"to'p nazorati asosan maydondagi ustunlikni belgilab berdi. {home_team} jamoasi yaratilgan vaziyatlardan "
            f"yaxshiroq foydalangan holda g'alabani qo'lga kiritdi.\n\n"
            f"Uchrashuvning eng yorqin daqiqalari va muhim pallalari ushbu natijani aniqlab berdi. "
            f"Ikkala jamoa murabbiylari ham o'yindan so'ng taktik o'zgarishlar haqida to'xtalib o'tishlari kutilmoqda."
        )

    async def generate_news_article(self, topic: str) -> Dict[str, Any]:
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
        generated = await self._generate(prompt)
        if generated:
            try:
                clean_text = generated.replace("```json", "").replace("```", "").strip()
                article = json.loads(clean_text)
                # Model kutilmagan shakl qaytarsa zaxira matnga tushamiz
                if all(key in article for key in ("title", "summary", "content")):
                    article.setdefault("tags", ["futbol"])
                    return article
                logger.warning("Gemini JSON'ida majburiy maydonlar yetishmayapti")
            except json.JSONDecodeError as exc:
                logger.warning("Gemini JSON'ini o'qib bo'lmadi: %s", exc)

        # Qoidaga asoslangan zaxira yangilik
        slug_topic = topic.lower().replace(" ", "-")
        return {
            "title": f"Dahshatli Transfer: {topic} bo'yicha yangi tafsilotlar",
            "summary": "Yevropa futbolida yangi mish-mishlar va rasmiy muzokaralar qizg'in pallaga kirdi. Batafsil bizning maqolamizda.",
            "content": (
                f"### Transfer Bozoridagi So'nggi Yangiliklar\n\n"
                f"Futbol olamida katta shov-shuvlarga sabab bo'layotgan **{topic}** masalasi kun tartibidagi eng muhim mavzu bo'lib turibdi.\n\n"
                f"Nufuzli insayderlarning xabar berishicha, jamoalar kelishuv shartlarini kelishib olishgan va yaqin kunlarda tibbiy ko'riklar rejalashtirilgan. "
                f"Muxlislar ushbu kelishuvning yakunlanishini sabrsizlik bilan kutishmoqda.\n\n"
                f"Batafsil yangiliklarni AI Football Hub Uzbekistan platformasida kuzatib boring!"
            ),
            "tags": ["transfer", "futbol", "breaking", slug_topic],
        }


@lru_cache
def get_ai_engine() -> AIEngineService:
    """FastAPI dependency: yagona umumiy AIEngineService nusxasi."""
    return AIEngineService()
