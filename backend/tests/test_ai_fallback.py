"""AI zaxira zanjiri: Gemini API -> Vertex AI -> o'zbekcha shablon.

Testlar tarmoqqa chiqmaydi — soxta klientlar ishlatiladi. Maqsad: zaxiraga
o'tish mantiqi to'g'ri ishlashini kafolatlash. (Haqiqiy Vertex ulanishi
qo'lda tekshirilgan; CI da hisob ma'lumotlari bo'lmaydi.)
"""

import pytest

from app.services.ai_engine import AIEngineService, Provider


class _Javob:
    def __init__(self, text):
        self.text = text


class _SoxtaModels:
    def __init__(self, javob=None, xato=None):
        self._javob = javob
        self._xato = xato
        self.chaqiruvlar = 0

    def generate_content(self, model, contents):
        self.chaqiruvlar += 1
        if self._xato:
            raise self._xato
        return _Javob(self._javob)


class _SoxtaKlient:
    def __init__(self, javob=None, xato=None):
        self.models = _SoxtaModels(javob, xato)


def _engine_with(*providers: Provider) -> AIEngineService:
    """Tarmoqqa chiqmaydigan dvigatel — manbalar qo'lda o'rnatiladi."""
    engine = AIEngineService.__new__(AIEngineService)
    engine.api_key = ""
    engine.model_name = "test-model"
    engine.providers = list(providers)
    engine._active_label = None
    engine.enabled = bool(providers)
    return engine


async def test_asosiy_ishlasa_zaxira_chaqirilmaydi():
    asosiy = _SoxtaKlient(javob="asosiy javob")
    zaxira = _SoxtaKlient(javob="zaxira javob")
    engine = _engine_with(
        Provider("Gemini API", asosiy, "m1"),
        Provider("Vertex AI", zaxira, "m2"),
    )

    assert await engine._generate("savol") == "asosiy javob"
    assert asosiy.models.chaqiruvlar == 1
    assert zaxira.models.chaqiruvlar == 0, "asosiy ishlaganda zaxira tegilmasligi kerak"


async def test_asosiy_xato_bersa_zaxiraga_otiladi():
    asosiy = _SoxtaKlient(xato=RuntimeError("401 UNAUTHENTICATED"))
    zaxira = _SoxtaKlient(javob="zaxira javob")
    engine = _engine_with(
        Provider("Gemini API", asosiy, "m1"),
        Provider("Vertex AI", zaxira, "m2"),
    )

    assert await engine._generate("savol") == "zaxira javob"
    assert zaxira.models.chaqiruvlar == 1
    assert engine._active_label == "Vertex AI"


async def test_asosiy_bosh_javob_bersa_ham_zaxiraga_otiladi():
    """Xato emas, lekin bo'sh javob — bu ham nosozlik hisoblanadi."""
    asosiy = _SoxtaKlient(javob="   ")
    zaxira = _SoxtaKlient(javob="zaxira javob")
    engine = _engine_with(
        Provider("Gemini API", asosiy, "m1"),
        Provider("Vertex AI", zaxira, "m2"),
    )

    assert await engine._generate("savol") == "zaxira javob"


async def test_ikkalasi_ishlamasa_bosh_satr():
    asosiy = _SoxtaKlient(xato=RuntimeError("401"))
    zaxira = _SoxtaKlient(xato=RuntimeError("404"))
    engine = _engine_with(
        Provider("Gemini API", asosiy, "m1"),
        Provider("Vertex AI", zaxira, "m2"),
    )

    assert await engine._generate("savol") == ""


async def test_manba_yoq_bolsa_shablon_qaytadi():
    """Foydalanuvchi hech qachon bo'sh kontent ko'rmasligi kerak."""
    engine = _engine_with()

    matn = await engine.generate_match_preview("Pakhtakor", "Navbahor", "Superliga")
    assert "Pakhtakor" in matn and "Navbahor" in matn
    assert len(matn) > 200, "shablon matn to'liq bo'lishi kerak"


async def test_hamma_manba_yiqilsa_ham_shablon_qaytadi():
    asosiy = _SoxtaKlient(xato=RuntimeError("401"))
    engine = _engine_with(Provider("Gemini API", asosiy, "m1"))

    matn = await engine.generate_match_preview("Arsenal", "Chelsea", "EPL")
    assert "Arsenal" in matn and "Chelsea" in matn


async def test_yangilik_json_buzuq_bolsa_shablon():
    """Model JSON o'rniga tushunarsiz matn qaytarsa ham maqola yaratilishi kerak."""
    asosiy = _SoxtaKlient(javob="bu JSON emas")
    engine = _engine_with(Provider("Gemini API", asosiy, "m1"))

    maqola = await engine.generate_news_article("Messi transferi")
    assert {"title", "summary", "content", "tags"} <= set(maqola)
    assert "Messi transferi" in maqola["title"]


@pytest.mark.parametrize(
    "javob,kutilgan",
    [
        ("  matn  ", "matn"),
        (None, ""),
        ("", ""),
    ],
)
async def test_javob_tozalanadi(javob, kutilgan):
    klient = _SoxtaKlient(javob=javob)
    engine = _engine_with(Provider("Gemini API", klient, "m1"))
    assert await engine._generate("savol") == kutilgan
