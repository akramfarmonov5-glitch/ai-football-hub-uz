"""Vaqt bilan ishlash uchun yagona kelishuv.

Qoida:
  * Bazada vaqt **naive UTC** ko'rinishda saqlanadi (SQLite timezone'ni
    qo'llab-quvvatlamaydi, shuning uchun "naive = UTC" deb kelishamiz).
  * Tashqariga (JSON javob) chiqayotganda **har doim timezone belgisi bilan**
    beriladi — `2026-07-05T01:29:37+00:00`.

Nima uchun muhim: timezone'siz ISO satrni brauzer MAHALLIY vaqt deb o'qiydi.
Shu sababli O'zbekistonda o'yin vaqtlari 5 soatga siljib ko'rinardi.

`datetime.utcnow()` esa Python 3.12+ da deprecated — bu yerdagi `utcnow()`
uning to'g'ri o'rnini bosadi.
"""

from datetime import datetime, timezone
from typing import Optional


def utcnow() -> datetime:
    """Hozirgi UTC vaqti, naive ko'rinishda — bazaga yozish uchun."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def as_utc(value: Optional[datetime]) -> Optional[datetime]:
    """Bazadan olingan naive qiymatga UTC belgisini qo'yadi.

    Allaqachon timezone'li bo'lsa — UTC ga o'giradi.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def to_naive_utc(value: Optional[datetime]) -> Optional[datetime]:
    """Tashqi manbadan kelgan (timezone'li) vaqtni bazaga yozish uchun tayyorlaydi."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)
