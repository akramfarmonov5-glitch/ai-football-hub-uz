import asyncio
import json
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Provider:
    """Matn generatsiya qiluvchi bitta manba."""

    label: str
    client: Any
    model: str


class AIEngineService:
    """Matn generatsiyasi: Gemini API -> Vertex AI -> o'zbekcha shablon.

    Uch qatlamli zaxira. Asosiy kalit ishlamay qolsa (limit tugadi, kalit
    o'chirildi, tarmoq uzildi) so'rov service account orqali Vertex AI ga
    yuboriladi. Ikkalasi ham ishlamasa shablonli matn qaytadi — sayt hech
    qachon bo'sh kontent ko'rsatmaydi.

    Muhim: Gemini SDK sinxron ishlaydi. Uni to'g'ridan-to'g'ri async endpointda
    chaqirish butun event loop'ni bloklaydi — ya'ni AI javobini kutayotgan
    10 soniyada API ham, jonli WebSocket yangilanishlari ham to'xtab qoladi.
    Shuning uchun har bir chaqiruv `asyncio.to_thread` orqali alohida oqimda
    bajariladi.
    """

    def __init__(self) -> None:
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        self.model_name = settings.GEMINI_MODEL

        self.providers: List[Provider] = []
        self._active_label: Optional[str] = None

        primary = self._build_api_key_provider()
        if primary:
            self.providers.append(primary)

        fallback = self._build_vertex_provider()
        if fallback:
            self.providers.append(fallback)

        self.enabled = bool(self.providers)
        if self.enabled:
            logger.info(
                "AI dvigateli yoqildi: %s",
                " -> ".join(f"{p.label} ({p.model})" for p in self.providers),
            )
        else:
            logger.info("AI manbasi sozlanmagan — shablonli matnlar ishlatiladi")

    # ------------------------------------------------------------------
    # Manbalarni tayyorlash
    # ------------------------------------------------------------------
    def _build_api_key_provider(self) -> Optional[Provider]:
        if not self.api_key:
            return None
        try:
            # SDK faqat kerak bo'lganda yuklanadi
            from google import genai

            return Provider("Gemini API", genai.Client(api_key=self.api_key), self.model_name)
        except Exception as exc:
            logger.warning("Gemini API klientini yaratib bo'lmadi: %s", exc)
            return None

    def _build_vertex_provider(self) -> Optional[Provider]:
        """Service account orqali Vertex AI klienti (zaxira yo'l)."""
        project = settings.vertex_project
        if not project:
            return None

        try:
            from google import genai

            credentials_path = settings.vertex_credentials_path
            credentials = None
            if credentials_path:
                from google.oauth2 import service_account

                credentials = service_account.Credentials.from_service_account_file(
                    str(credentials_path),
                    scopes=["https://www.googleapis.com/auth/cloud-platform"],
                )
                logger.info("Vertex uchun service account: %s", credentials_path.name)
            else:
                # Kalit fayli ko'rsatilmagan — muhitdagi standart hisob (ADC)
                logger.info("Vertex uchun ADC (standart hisob ma'lumotlari) ishlatiladi")

            client = genai.Client(
                vertexai=True,
                project=project,
                location=settings.VERTEX_LOCATION,
                credentials=credentials,
            )
            return Provider("Vertex AI", client, settings.vertex_model)
        except Exception as exc:
            logger.warning("Vertex AI zaxirasini yoqib bo'lmadi: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Ichki yordamchi
    # ------------------------------------------------------------------
    async def _generate(self, prompt: str) -> str:
        """Manbalarni navbat bilan sinaydi. Hech biri ishlamasa bo'sh satr."""
        for provider in self.providers:
            try:
                response = await asyncio.to_thread(
                    provider.client.models.generate_content,
                    model=provider.model,
                    contents=prompt,
                )
                text = (response.text or "").strip()
                if text:
                    # Manba almashganini bir marta qayd etamiz, har chaqiruvda emas
                    if self._active_label != provider.label:
                        logger.info("AI manbasi: %s (%s)", provider.label, provider.model)
                        self._active_label = provider.label
                    return text
                logger.warning("%s bo'sh javob qaytardi", provider.label)
            except Exception as exc:
                logger.warning("%s xatosi: %s", provider.label, exc)

        if self.providers:
            logger.warning("Barcha AI manbalari ishlamadi — shablonli matn ishlatiladi")
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

    async def translate_to_uzbek(self, text: str, subject: str = "") -> str:
        """Matnni o'zbek tiliga o'giradi. Muvaffaqiyatsiz bo'lsa bo'sh satr.

        Jamoa tavsiflari manbadan inglizcha keladi. Bo'sh satr qaytsa
        chaqiruvchi asl matnni ko'rsatadi — foydalanuvchi hech bo'lmasa
        biror ma'lumot ko'radi.
        """
        if not text or not text.strip():
            return ""

        kontekst = f" ({subject} futbol klubi haqida)" if subject else ""
        prompt = f"""
        Quyidagi matnni{kontekst} o'zbek tiliga tarjima qiling.

        Talablar:
        - Faqat tarjimani qaytaring, hech qanday izoh yoki muqaddima yozmang
        - Futbol atamalarini o'zbek tilida qabul qilingan shaklda ishlating
        - Klub va shahar nomlarini o'zbek tilida odatda qanday yozilsa shunday yozing
        - Xatboshilar tuzilishini saqlang
        - Matnni qisqartirmang va o'zingizdan ma'lumot qo'shmang

        Matn:
        {text}
        """
        return await self._generate(prompt)

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
