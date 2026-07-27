"""O'yin hayot sikli: NS -> LIVE -> FT va jadvalning to'lib turishi.

Ilgari 3 ta namunaviy o'yin 90-daqiqaga yetgach sayt abadiy muzlab qolardi —
yangi o'yin paydo bo'lishining hech qanday yo'li yo'q edi.
"""

from sqlalchemy import func, select

from app.core.clock import utcnow
from app.models.match import Match
from app.services.fixtures import UPCOMING_TARGET, pair_key
from app.services.football_api import FootballAPIService


async def _statuses(db):
    rows = await db.execute(select(Match.status, func.count()).group_by(Match.status))
    return dict(rows.all())


async def test_bosh_bazada_jadval_toldiriladi(db):
    service = FootballAPIService(db)
    await service.advance_matches(allow_real_fetch=False)

    assert (await _statuses(db)).get("NS") == UPCOMING_TARGET


async def test_vaqti_kelgan_oyin_boshlanadi(db):
    service = FootballAPIService(db)
    await service.advance_matches(allow_real_fetch=False)

    upcoming = (await db.execute(select(Match).where(Match.status == "NS").limit(1))).scalar_one()
    upcoming.match_time = utcnow()
    db.add(upcoming)
    await db.commit()

    await FootballAPIService(db).advance_matches(allow_real_fetch=False)

    started = await db.get(Match, upcoming.id)
    assert started.status == "LIVE"
    assert started.minute >= 1
    assert started.stats is not None, "o'yin boshlanganda statistika paydo bo'lishi kerak"
    assert started.win_probability is not None


async def test_oyin_tugaydi_va_jadval_qayta_toladi(db):
    service = FootballAPIService(db)
    await service.advance_matches(allow_real_fetch=False)

    match = (await db.execute(select(Match).where(Match.status == "NS").limit(1))).scalar_one()
    match.match_time = utcnow()
    db.add(match)
    await db.commit()
    match_id = match.id

    for _ in range(95):
        await FootballAPIService(db).advance_matches(allow_real_fetch=False)

    finished = await db.get(Match, match_id)
    assert finished.status == "FT"
    assert finished.minute >= 90

    # Tugagandan keyin ham jadvalda bo'lajak o'yinlar turishi kerak
    assert (await _statuses(db)).get("NS") == UPCOMING_TARGET


async def test_jadvaldagi_juftliklar_takrorlanmaydi(db):
    await FootballAPIService(db).advance_matches(allow_real_fetch=False)

    rows = await db.execute(
        select(Match.home_team_name, Match.away_team_name).where(Match.status == "NS")
    )
    pairs = [pair_key(h, a) for h, a in rows.all()]
    assert len(pairs) == len(set(pairs)), "bir xil bahs ikki marta rejalashtirilgan"


async def test_jamoa_ozi_bilan_oynamaydi(db):
    await FootballAPIService(db).advance_matches(allow_real_fetch=False)

    rows = await db.execute(select(Match.home_team_name, Match.away_team_name))
    for home, away in rows.all():
        assert home != away


async def test_gollar_qayd_etiladi(db):
    """Gol urilganda hisob ham, xronologiya ham, xabarnoma ro'yxati ham yangilanadi."""
    await FootballAPIService(db).advance_matches(allow_real_fetch=False)

    match = (await db.execute(select(Match).where(Match.status == "NS").limit(1))).scalar_one()
    match.match_time = utcnow()
    db.add(match)
    await db.commit()
    match_id = match.id

    total_goals_reported = 0
    for _ in range(95):
        service = FootballAPIService(db)
        await service.advance_matches(allow_real_fetch=False)
        total_goals_reported += sum(1 for m, _ in service.new_goals if m.id == match_id)

    finished = await db.get(Match, match_id)
    goals_in_timeline = sum(1 for e in (finished.timeline or []) if e["type"] == "Goal")

    assert goals_in_timeline == total_goals_reported
    assert finished.score_home + finished.score_away == goals_in_timeline
