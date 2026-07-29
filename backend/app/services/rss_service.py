"""Stadion.uz RSS Feed'dan yangiliklarni tortish xizmati.

Stadion.uz RSS tasmasidan eng so'nggi futbol yangiliklarini avtomatik
tortib oladi, Kirillcha matnlarni Lotinchaga (AI yoki zaxira algoritmi bilan)
o'tkazadi va bazaga hamda Telegram kanalga avtopost qiladi.
"""

import asyncio
import html
import logging
import re
import xml.etree.ElementTree as ET
from typing import List, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.news import slugify
from app.models.news import News
from app.services.ai_engine import get_ai_engine
from app.services.notifier import notify_news_item

logger = logging.getLogger(__name__)

STADION_RSS_URL = "https://stadion.uz/uz/news/rss"

# DIQQAT: bu o'zbek lotin alifbosi, rus transliteratsiyasi emas.
# Asosiy farq: Ж -> J (ruschada "Zh"). Ilgari shu xato tufayli
# "жамоа" -> "zhamoa", "ЖЧ" -> "ZhCh", "режа" -> "rezha" chiqardi.
CYRILLIC_TO_LATIN_MAP = {
    "А": "A", "а": "a", "Б": "B", "б": "b", "В": "V", "в": "v", "Г": "G", "г": "g",
    "Д": "D", "д": "d", "Е": "E", "е": "e", "Ё": "Yo", "ё": "yo", "Ж": "J", "ж": "j",
    "З": "Z", "з": "z", "И": "I", "и": "i", "Й": "Y", "й": "y", "К": "K", "к": "k",
    "Л": "L", "л": "l", "М": "M", "м": "m", "Н": "N", "н": "n", "О": "O", "о": "o",
    "П": "P", "п": "p", "Р": "R", "р": "r", "С": "S", "с": "s", "Т": "T", "т": "t",
    "У": "U", "у": "u", "Ф": "F", "ф": "f", "Х": "X", "х": "x", "Ц": "Ts", "ц": "ts",
    "Ч": "Ch", "ч": "ch", "Ш": "Sh", "ш": "sh", "Ъ": "'", "ъ": "'", "Ь": "", "ь": "",
    "Э": "E", "э": "e", "Ю": "Yu", "ю": "yu", "Я": "Ya", "я": "ya",
    "Ў": "O'", "ў": "o'", "Қ": "Q", "қ": "q", "Ғ": "G'", "ғ": "g'", "Ҳ": "H", "ҳ": "h"
}


def cyrillic_to_latin(text: str) -> str:
    """O'zbekcha kirillcha matnni lotinchaga o'tkazuvchi zaxira funksiya."""
    if not text:
        return ""
    result = []
    for char in text:
        result.append(CYRILLIC_TO_LATIN_MAP.get(char, char))
    return "".join(result)


def clean_html(text: str) -> str:
    """HTML teglari va belgilarini (&laquo;, &raquo;, &quot;) tozalaydi.

    Teglar olib tashlangach yana bir marta ochiladi: manba ba'zan ikki
    marta kodlangan matn beradi (`&amp;laquo;`), bir marta ochish esa
    `&laquo;` ni matn ichida qoldirib ketardi va sayt uni shundayligicha
    ko'rsatardi.
    """
    if not text:
        return ""

    clean = re.sub(r"<[^>]+>", " ", html.unescape(text))
    clean = html.unescape(clean)
    return re.sub(r"\s+", " ", clean).strip()


class RSSFeedService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_and_ingest(self, limit: int = 10) -> int:
        """RSS tasmadan yangi maqolalarni yuklaydi va saqlaydi.
        
        Qaytaradi: yangi qo'shilgan maqolalar soni.
        """
        try:
            async with httpx.AsyncClient(timeout=15.0, headers={"User-Agent": "Mozilla/5.0"}) as client:
                response = await client.get(STADION_RSS_URL)
                response.raise_for_status()
                xml_content = response.content
        except Exception as exc:
            logger.warning("Stadion.uz RSS yuklashda xato: %s", exc)
            return 0

        try:
            root = ET.fromstring(xml_content)
            items = root.findall(".//item")
        except Exception as exc:
            logger.warning("Stadion.uz RSS XML tahlilida xato: %s", exc)
            return 0

        added_count = 0
        ai = get_ai_engine()

        for item in items[:limit]:
            title_node = item.find("title")
            link_node = item.find("link")
            desc_node = item.find("description")
            enclosure_node = item.find("enclosure")

            if title_node is None or not title_node.text or link_node is None or not link_node.text:
                continue

            raw_title = html.unescape(title_node.text.strip())
            source_url = link_node.text.strip()

            # Takroriy yangilikni tekshirish.
            # Faqat manba havolasi bo'yicha: `raw_title` kirillcha, bazadagi
            # sarlavhalar esa lotinchada saqlanadi — ularni solishtirish
            # hech qachon mos kelmasdi va tekshiruv aldamchi edi.
            existing = await self.db.scalar(
                select(News.id).where(News.source_url == source_url)
            )
            if existing:
                continue

            raw_desc = clean_html(desc_node.text if desc_node is not None else "")
            
            # Rasm URL manzilini olish
            image_url = None
            if enclosure_node is not None:
                img_path = enclosure_node.attrib.get("url", "")
                if img_path:
                    if img_path.startswith("http"):
                        image_url = img_path
                    else:
                        image_url = f"https://stadion.uz/images/news/{img_path}"

            # AI orqali Kirillchani Lotinchaga va chiroyli tahlilga o'tkazish
            latin_title = ""
            latin_summary = ""
            tags = ["#futbol", "#yangiliklar", "#stadion"]

            if ai and ai.enabled:
                try:
                    prompt = (
                        f"Quyidagi o'zbekcha kirillcha futbol yangiligini lotin alifbosiga o'tkaz, "
                        f"chiroyli va jozibador sarlavha hamda 2-3 jumlalik qisqacha mazmun shakllantir.\n"
                        f"Format:\nSarlavha: <lotincha sarlavha>\nMazmun: <lotincha mazmun>\nTeglar: #teg1 #teg2\n\n"
                        f"Original Sarlavha: {raw_title}\nOriginal Mazmun: {raw_desc}"
                    )
                    res = await ai._generate(prompt)
                    if res:
                        lines = res.strip().split("\n")
                        for line in lines:
                            if line.lower().startswith("sarlavha:"):
                                latin_title = line.split(":", 1)[1].strip()
                            elif line.lower().startswith("mazmun:"):
                                latin_summary = line.split(":", 1)[1].strip()
                            elif line.lower().startswith("teglar:"):
                                tags_str = line.split(":", 1)[1].strip()
                                tags = [t.strip() for t in tags_str.split() if t.startswith("#")]
                except Exception as exc:
                    # Jimgina yutib yubormaymiz: ilgari shu yerda mavjud
                    # bo'lmagan metod chaqirilgani sababli AI hech qachon
                    # ishlamagan, log'da esa hech narsa ko'rinmagan.
                    logger.warning("RSS: AI boyitish ishlamadi: %s", exc)

            if not latin_title:
                latin_title = cyrillic_to_latin(raw_title)
            if not latin_summary:
                latin_summary = cyrillic_to_latin(raw_desc)

            base_slug = slugify(latin_title)
            slug = base_slug
            counter = 1
            while await self.db.scalar(select(News).where(News.slug == slug)):
                slug = f"{base_slug}-{counter}"
                counter += 1

            new_article = News(
                title=latin_title,
                slug=slug,
                summary=latin_summary,
                content=f"{latin_summary}\n\nManba: {source_url}",
                image_url=image_url,
                source_url=source_url,
                tags=tags,
                is_published=True,
            )

            self.db.add(new_article)
            await self.db.commit()
            added_count += 1
            logger.info("RSS'dan yangi maqola saqlandi: %s", latin_title)

            # Telegram kanalga avtopost qilish (rasm va matn bilan)
            try:
                await notify_news_item(latin_title, latin_summary, slug, image_url=image_url)
            except Exception:
                pass

        return added_count


async def run_rss_loop():
    """15 daqiqada bir marotaba RSS tasmadan yangiliklarni tortuvchi fonda ishlovchi sikl."""
    logger.info("RSS Feed Ingestion sikli ishga tushirildi...")
    from app.core.database import AsyncSessionLocal

    while True:
        try:
            async with AsyncSessionLocal() as db:
                count = await RSSFeedService(db).fetch_and_ingest()
                if count > 0:
                    logger.info("RSS: %d ta yangi maqola joylandi.", count)
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.error("RSS Ingestion siklida kutilmagan xato: %s", exc)

        await asyncio.sleep(900)  # 15 daqiqa (900 soniya)
