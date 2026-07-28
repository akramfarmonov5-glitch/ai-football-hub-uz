"""Markazlashtirilgan o'zbekcha tarjimalar lug'ati.

Liga va jamoa nomlarini o'zbek tiliga o'girish uchun.
"""

LEAGUE_TRANSLATIONS = {
    "Uzbekistan Super League": "O'zbekiston Superligasi",
    "UEFA Champions League": "UEFA Chempionlar Ligasi",
    "English Premier League": "Angliya Premyer-ligasi",
    "Premier League": "Angliya Premyer-ligasi",
    "La Liga": "Ispaniya La Ligasi",
    "Spanish La Liga": "Ispaniya La Ligasi",
    "Serie A": "Italiya A Seriyasi",
    "Italian Serie A": "Italiya A Seriyasi",
    "Bundesliga": "Germaniya Bundesligasi",
    "German Bundesliga": "Germaniya Bundesligasi",
    "Ligue 1": "Fransiya 1-Ligasi",
    "French Ligue 1": "Fransiya 1-Ligasi",
    "Turkish Super Lig": "Turkiya Superligasi",
}

TEAM_TRANSLATIONS = {
    # O'zbekiston klublari
    "Neftchi Fergana": "Neftchi Farg'ona",
    "Surkhon Termez": "Surxon Termiz",
    "Qizilqum Zarafshon": "Qizilqum Zarafshon",
    "Pakhtakor Tashkent": "Paxtakor Toshkent",
    "Bunyodkor Tashkent": "Bunyodkor Toshkent",
    "Lokomotiv Tashkent": "Lokomotiv Toshkent",
    "Dinamo Samarkand": "Dinamo Samarqand",
    "Nasaf": "Nasaf Qarshi",
    "Navbahor Namangan": "Navbahor Namangan",
    "Xorazm Urganch": "Xorazm Urganch",
    "Andijon": "Andijon",
    "Metallurg Bekabad": "Metallurg Bekobod",
    "Sogdiana Jizzakh": "So'gdiyona Jizzax",
    "Olympic Tashkent": "Olimpik Toshkent",
    "AGMK Almalyk": "OKMK Olmaliq",
    "Bukhara": "Buxoro",
    # Yevropa klublari
    "Górnik Zabrze": "Gurnik Zabje",
    "Fenerbahçe": "Fenerbaxche",
    "Hapoel Be'er Sheva": "Xapoel Beer-Sheva",
    "Vikingur Reykjavik": "Vikingur Reykyavik",
    "Lech Poznań": "Lex Poznan",
    "AGF Aarhus": "AGF Orxus",
    "Heart of Midlothian": "Xarts",
    "Sturm Graz": "Shturm Grats",
    "Dinamo Zagreb": "Dinamo Zagreb",
    "Thun": "Tun",
    "Real Madrid": "Real Madrid",
    "Barcelona": "Barselona",
    "Manchester City": "Manchester Siti",
    "Manchester United": "Manchester Yunayted",
    "Arsenal": "Arsenal",
    "Liverpool": "Liverpul",
    "Chelsea": "Chelsi",
    "Bayern Munich": "Bavariya",
    "Borussia Dortmund": "Borussiya Dortmund",
    "Paris Saint Germain": "PSJ",
    "Juventus": "Yuventus",
    "Inter": "Inter",
    "AC Milan": "Milan",
}


def translate_league(name: str) -> str:
    if not name:
        return ""
    clean = name.strip()
    return LEAGUE_TRANSLATIONS.get(clean, clean)


def translate_team(name: str) -> str:
    if not name:
        return ""
    clean = name.strip()
    return TEAM_TRANSLATIONS.get(clean, clean)
