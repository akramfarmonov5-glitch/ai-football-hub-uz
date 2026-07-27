"""Slug yasash: har qanday sarlavhadan yaroqli URL chiqishi kerak.

Ilgari lotin bo'lmagan sarlavha (masalan kirill) bo'sh slug berardi va
maqola manzilsiz qolardi.
"""

from app.api.endpoints.news import slugify


def test_oddiy_sarlavha():
    assert slugify("Mbappe Real Madridga o'tdi") == "mbappe-real-madridga-otdi"


def test_apostroflar_tushiriladi():
    assert slugify("O'zbekiston g'alaba qozondi") == "ozbekiston-galaba-qozondi"


def test_maxsus_belgilar_olib_tashlanadi():
    assert slugify("Real 3:2 Barca! (El Clasico)") == "real-32-barca-el-clasico"


def test_kirill_sarlavhada_zaxira_nom():
    slug = slugify("Чемпионат Узбекистана")
    assert slug, "bo'sh slug qaytmasligi kerak"
    assert slug.startswith("maqola-")


def test_bosh_sarlavhada_zaxira_nom():
    assert slugify("!!!").startswith("maqola-")


def test_juda_uzun_sarlavha_qisqartiriladi():
    slug = slugify("soz " * 100)
    assert len(slug) <= 80
    assert not slug.endswith("-")
