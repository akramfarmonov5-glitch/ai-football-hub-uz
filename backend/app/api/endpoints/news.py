import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.clock import utcnow
from app.core.database import get_async_db
from app.core.security import verify_admin
from app.models.news import News
from app.schemas.news import NewsResponse, NewsCreate

router = APIRouter()

# O'zbekcha harflarni lotin ekvivalentiga o'tkazish (o' -> o, g' -> g, ...)
_TRANSLITERATION = str.maketrans({"‘": "", "’": "", "'": "", "`": "", "ʻ": "", "ʼ": ""})


def slugify(text: str) -> str:
    """Sarlavhadan URL uchun yaroqli slug yasaydi.

    Sarlavha butunlay lotin bo'lmagan harflardan iborat bo'lsa (masalan kirill),
    ilgari bo'sh slug chiqib, maqola manzilsiz qolardi — endi zaxira nom beriladi.
    """
    text = text.lower().translate(_TRANSLITERATION)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    if not text:
        text = f"maqola-{utcnow().strftime('%Y%m%d-%H%M%S')}"
    return text[:80].strip("-")

@router.get("/", response_model=List[NewsResponse])
async def get_news(
    db: AsyncSession = Depends(get_async_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = await db.execute(
        select(News)
        .where(News.is_published == True)
        .order_by(News.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()

@router.get("/{slug}", response_model=NewsResponse)
async def get_news_detail(slug: str, db: AsyncSession = Depends(get_async_db)):
    news = await db.scalar(select(News).where(News.slug == slug))
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")
    return news

# Maqola yaratish — faqat admin tokeni bilan (aks holda har kim saytga
# o'zi xohlagan kontentni chop eta olardi).
@router.post("/", response_model=NewsResponse, dependencies=[Depends(verify_admin)])
async def create_news_article(news_in: NewsCreate, db: AsyncSession = Depends(get_async_db)):
    base_slug = slugify(news_in.title)
    # Check for uniqueness
    slug = base_slug
    counter = 1
    while await db.scalar(select(News).where(News.slug == slug)):
        slug = f"{base_slug}-{counter}"
        counter += 1

    db_news = News(
        title=news_in.title,
        slug=slug,
        summary=news_in.summary,
        content=news_in.content,
        image_url=news_in.image_url,
        source_url=news_in.source_url,
        tags=news_in.tags,
        is_published=news_in.is_published
    )
    db.add(db_news)
    await db.commit()
    await db.refresh(db_news)
    return db_news
