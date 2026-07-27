"""Gol xabarnomasi: kimga yuborilishi va xabar matni."""

from app.models.match import Match
from app.models.user import User
from app.services.notifier import _find_subscribers, build_goal_message, notify_goal


def _match() -> Match:
    return Match(
        id=1,
        league_id=39,
        league_name="English Premier League",
        home_team_name="Arsenal",
        away_team_name="Chelsea",
        status="LIVE",
        score_home=1,
        score_away=0,
        minute=23,
    )


GOAL_EVENT = {"time": 23, "type": "Goal", "detail": "Saka (Gol!)", "team": "home"}


def test_xabar_matni_toliq():
    text = build_goal_message(_match(), GOAL_EVENT)

    assert "GOL!" in text
    assert "Arsenal" in text
    assert "1 - 0" in text
    assert "23-daqiqa" in text
    assert "Saka" in text
    assert "/matches/1" in text


def test_markdown_belgilari_ekranlanadi():
    """Jamoa nomida `_` bo'lsa Telegram formatlashi buzilmasligi kerak."""
    match = _match()
    match.home_team_name = "FC_Test*Team"
    text = build_goal_message(match, GOAL_EVENT)
    assert "FC\\_Test\\*Team" in text


async def test_faqat_tegishli_obunachilar_topiladi(db):
    db.add_all(
        [
            User(telegram_id="1", username="arsenal_fan", favorite_team="Arsenal"),
            User(telegram_id="2", username="chelsea_fan", favorite_team="Chelsea"),
            User(telegram_id="3", username="madrid_fan", favorite_team="Real Madrid"),
            User(telegram_id="4", username="hech_kim", favorite_team=None),
        ]
    )
    await db.commit()

    subscribers = await _find_subscribers(db, _match())
    names = {u.username for u in subscribers}

    assert names == {"arsenal_fan", "chelsea_fan"}, "faqat o'yindagi jamoalar muxlislari"


async def test_bot_tokeni_yoq_bolsa_jimgina_otkaziladi(db):
    """TELEGRAM_BOT_TOKEN sozlanmagan (test muhitida) — xato bermasligi kerak."""
    db.add(User(telegram_id="1", username="fan", favorite_team="Arsenal"))
    await db.commit()

    sent = await notify_goal(db, _match(), GOAL_EVENT)
    assert sent == 0
