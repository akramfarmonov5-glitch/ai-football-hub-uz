"""RSS xizmati: transliteratsiya va HTML tozalash.

Tarmoqqa chiqilmaydi — faqat toza funksiyalar tekshiriladi.
"""

import pytest

from app.services.rss_service import clean_html, cyrillic_to_latin


# ---------------------------------------------------------------------------
# Transliteratsiya
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "kirill,kutilgan",
    [
        # Asosiy xato bo'lgan joy: Ж -> J (ruschadagi "Zh" emas)
        ("жамоа", "jamoa"),
        ("Жаҳон", "Jahon"),
        ("режа", "reja"),
        ("ЖЧ", "JCh"),
        ("Жон Жонс", "Jon Jons"),
        # O'zbekchaga xos harflar
        ("Ўзбекистон", "O'zbekiston"),
        ("Қизилқум", "Qizilqum"),
        ("Ғалаба", "G'alaba"),
        ("Тошкент", "Toshkent"),
        ("Пахтакор", "Paxtakor"),
        # Boshqa tipik harflar
        ("Чемпион", "Chempion"),
        ("Шаҳар", "Shahar"),
        ("Ёшлар", "Yoshlar"),
        ("Юлдуз", "Yulduz"),
        ("Ярим", "Yarim"),
    ],
)
def test_kirilldan_lotinga(kirill, kutilgan):
    assert cyrillic_to_latin(kirill) == kutilgan


def test_lotin_matn_tegilmaydi():
    assert cyrillic_to_latin("Pakhtakor 2-1") == "Pakhtakor 2-1"


def test_bosh_matn():
    assert cyrillic_to_latin("") == ""
    assert cyrillic_to_latin(None) == ""


def test_tinish_belgilari_saqlanadi():
    assert cyrillic_to_latin("«Пахтакор» - 2:1") == "«Paxtakor» - 2:1"


# ---------------------------------------------------------------------------
# HTML tozalash
# ---------------------------------------------------------------------------


def test_html_teglari_olib_tashlanadi():
    assert clean_html("<p>Salom <b>dunyo</b></p>") == "Salom dunyo"


def test_html_obyektlari_ochiladi():
    assert clean_html("&laquo;Paxtakor&raquo;") == "«Paxtakor»"
    assert clean_html("&quot;Nasaf&quot;") == '"Nasaf"'
    assert clean_html("Bir &amp; ikki") == "Bir & ikki"


def test_ortiqcha_boshliqlar_qisqaradi():
    assert clean_html("Bir\n\n  ikki   uch") == "Bir ikki uch"


def test_bosh_html():
    assert clean_html("") == ""
    assert clean_html(None) == ""
