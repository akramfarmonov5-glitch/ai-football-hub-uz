"""AI matnidan Markdown belgilarini tozalash.

Nima uchun kerak: matn ikki joyda ishlatiladi va ikkalasi ham Markdown
o'qimaydi — sayt uni oddiy tekst sifatida chiqaradi, Telegram esa o'z
formatlashiga ega. Tozalanmasa `**Dinamo**` shundayligicha ko'rinadi.
"""

import pytest

from app.services.ai_engine import AIEngineService, Provider, strip_markdown


@pytest.mark.parametrize(
    "kiritma,kutilgan",
    [
        ("**Paxtakor** g'alaba qozondi", "Paxtakor g'alaba qozondi"),
        ("__Nasaf__ jamoasi", "Nasaf jamoasi"),
        ("### Sarlavha", "Sarlavha"),
        ("# Katta sarlavha", "Katta sarlavha"),
        ("`kod`", "kod"),
        ("```blok```", "blok"),
        # Bir nechta belgi birga
        ("**Real** va **Barsa**", "Real va Barsa"),
        # Bezaksiz matn tegilmaydi
        ("Oddiy matn", "Oddiy matn"),
        ("2 * 3 = 6", "2 * 3 = 6"),
    ],
)
def test_belgilar_tozalanadi(kiritma, kutilgan):
    assert strip_markdown(kiritma) == kutilgan


def test_royxat_nuqtaga_aylanadi():
    matn = "Sabablar:\n* birinchi\n* ikkinchi"
    assert strip_markdown(matn) == "Sabablar:\n• birinchi\n• ikkinchi"


def test_bir_nechta_qatorli_qalin():
    matn = "**Birinchi qator\nva ikkinchisi**"
    assert strip_markdown(matn) == "Birinchi qator\nva ikkinchisi"


def test_xatboshilar_saqlanadi():
    matn = "**Birinchi.**\n\nIkkinchi xatboshi."
    assert strip_markdown(matn) == "Birinchi.\n\nIkkinchi xatboshi."


def test_bosh_matn():
    assert strip_markdown("") == ""
    assert strip_markdown(None) == ""


# ---------------------------------------------------------------------------
# Generatsiya natijasi tozalanadimi
# ---------------------------------------------------------------------------


class _Javob:
    def __init__(self, text):
        self.text = text


class _SoxtaKlient:
    def __init__(self, javob):
        self.models = type("M", (), {"generate_content": lambda s, model, contents: _Javob(javob)})()


def _engine(javob):
    engine = AIEngineService.__new__(AIEngineService)
    engine.api_key = ""
    engine.model_name = "test"
    engine.providers = [Provider("Test", _SoxtaKlient(javob), "m")]
    engine._active_label = None
    engine.enabled = True
    return engine


async def test_oyinoldi_tahlili_tozalanadi():
    engine = _engine("**Paxtakor** bugun kuchli.")
    matn = await engine.generate_match_preview("Paxtakor", "Nasaf", "Superliga")
    assert "**" not in matn
    assert matn == "Paxtakor bugun kuchli."


async def test_oyindan_keyingi_tahlil_tozalanadi():
    engine = _engine("### Xulosa\n**Nasaf** yutdi.")
    matn = await engine.generate_post_match_analysis("Nasaf", "AGMK", "2-1", {}, [])
    assert "**" not in matn and "###" not in matn


async def test_tarjima_tozalanadi():
    engine = _engine("**Fenerbahce** — Turkiya klubi.")
    assert "**" not in await engine.translate_to_uzbek("text", "Fenerbahce")


async def test_yangilik_maydonlari_tozalanadi():
    """Model ko'rsatmaga qaramay Markdown qo'shishi mumkin."""
    engine = _engine(
        '{"title": "**Katta** xabar", "summary": "__Qisqacha__",'
        ' "content": "### Sarlavha\\n**Matn**", "tags": ["a"]}'
    )
    maqola = await engine.generate_news_article("transfer")

    assert maqola["title"] == "Katta xabar"
    assert maqola["summary"] == "Qisqacha"
    assert "**" not in maqola["content"] and "###" not in maqola["content"]


async def test_zaxira_shablonlarda_markdown_yoq():
    """AI ishlamaganda ham matn toza bo'lishi kerak."""
    engine = AIEngineService.__new__(AIEngineService)
    engine.api_key = ""
    engine.model_name = "test"
    engine.providers = []
    engine._active_label = None
    engine.enabled = False

    preview = await engine.generate_match_preview("Paxtakor", "Nasaf", "Superliga")
    analysis = await engine.generate_post_match_analysis("Paxtakor", "Nasaf", "1-0", {}, [])
    article = await engine.generate_news_article("Messi")

    for matn in (preview, analysis, article["content"], article["title"]):
        assert "**" not in matn, f"shablonda Markdown qolgan: {matn[:60]}"
        assert "###" not in matn
