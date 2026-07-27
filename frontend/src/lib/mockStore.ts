export interface Match {
  id: number;
  league_id: number;
  league_name: string;
  home_team_name: string;
  away_team_name: string;
  home_team_logo: string;
  away_team_logo: string;
  status: string;
  score_home: number;
  score_away: number;
  match_time: string;
  minute: number;
  lineups?: { home: string[]; away: string[] };
  timeline?: { time: number; type: string; detail: string; team: string }[];
  stats?: { possession: { home: number; away: number }; shots: { home: number; away: number }; xG: { home: number; away: number } };
  ai_preview?: string;
  ai_analysis?: string;
  win_probability?: { home: number; draw: number; away: number };
}

export interface NewsItem {
  id: number;
  title: string;
  slug: string;
  summary: string;
  content: string;
  image_url?: string;
  source_url?: string;
  created_at: string;
  tags: string[];
}

const DEFAULT_NEWS: NewsItem[] = [
  {
    id: 1,
    title: "Dahshatli Transfer: Mbappe Real Madriddagi debyuti haqida gapirdi",
    slug: "mbappe-real-madrid-debyut",
    summary: "Kilian Mbappe o'zining qirollik klubidagi ilk taassurotlari va kelajakdagi maqsadlari bilan o'rtoqlashdi.",
    content: "Kilian Mbappe bugun matbuot anjumanida jurnalistlar savollariga javob berdi. U o'zining ilk o'yinidan juda mamnun ekanini va bu shunchaki boshlanishi ekanini ta'kidladi.\n\n'Bu bolalikdagi orzuim edi. Real Madrid libosida maydonga tushish menga o'zgacha shijoat beradi,' - dedi frantsiyalik yulduz.",
    created_at: new Date().toISOString(),
    tags: ["transfer", "real-madrid", "mbappe"]
  },
  {
    id: 2,
    title: "O'zbekiston Superligasi: Nasaf va Navbahor chempionlik kurashida",
    slug: "uzbekistan-superliga-nasaf-navbahor",
    summary: "Nasaf va Navbahor jamoalari o'rtasidagi so'nggi uchrashuvlardan keyin chempionlik poygasi yanada qizg'in tus oldi.",
    content: "O'zbekiston Superligasining qoldirilgan turlaridan so'ng turnir jadvalida keskin kurash yuzaga keldi. Nasaf jamoasi peshqadamlikni saqlab turgan bo'lsa-da, Navbahor ularni ta'qib qilmoqda.\n\nEkspertlar fikriga ko'ra, keyingi o'zaro to'qnashuv turnir taqdirini hal qilishi mumkin.",
    created_at: new Date().toISOString(),
    tags: ["superliga", "nasaf", "navbahor"]
  }
];

const DEFAULT_MATCHES: Match[] = [
  {
    id: 2001,
    league_id: 140,
    league_name: "La Liga",
    home_team_name: "Real Madrid",
    away_team_name: "Barcelona",
    home_team_logo: "https://media.api-sports.io/football/teams/541.png",
    away_team_logo: "https://media.api-sports.io/football/teams/529.png",
    status: "FT",
    score_home: 3,
    score_away: 2,
    match_time: new Date(Date.now() - 3600 * 1000 * 3).toISOString(),
    minute: 90,
    lineups: {
      home: ["Courtois", "Carvajal", "Militao", "Rudiger", "Mendy", "Valverde", "Tchouameni", "Bellingham", "Rodrygo", "Mbappe", "Vinicius Jr"],
      away: ["Ter Stegen", "Kounde", "Araujo", "Cubarsi", "Balde", "Pedri", "Gundogan", "De Jong", "Yamal", "Lewandowski", "Raphinha"]
    },
    timeline: [
      { time: 12, type: "Goal", detail: "Lewandowski (Assist: Yamal)", team: "away" },
      { time: 32, type: "Goal", detail: "Mbappe (Penalty)", team: "home" },
      { time: 58, type: "Goal", detail: "Vinicius Jr", team: "home" },
      { time: 76, type: "Goal", detail: "Raphinha", team: "away" },
      { time: 89, type: "Goal", detail: "Bellingham (Assist: Vinicius Jr)", team: "home" }
    ],
    stats: {
      possession: { home: 52, away: 48 },
      shots: { home: 16, away: 12 },
      xG: { home: 2.1, away: 1.7 }
    },
    win_probability: { home: 100, draw: 0, away: 0 },
    ai_preview: "El Clasico o'yinida shiddatli to'qnashuv kutilmoqda. Ikkala jamoa ham hujumkor futbol tarafdori.",
    ai_analysis: "Ajoyib va gollarga boy El Clasico guvohi bo'ldik. Jude Bellingham so'nggi daqiqalarda g'alaba golini kiritdi."
  },
  {
    id: 2002,
    league_id: 39,
    league_name: "English Premier League",
    home_team_name: "Arsenal",
    away_team_name: "Manchester City",
    home_team_logo: "https://media.api-sports.io/football/teams/42.png",
    away_team_logo: "https://media.api-sports.io/football/teams/50.png",
    status: "LIVE",
    score_home: 1,
    score_away: 1,
    match_time: new Date(Date.now() - 60000 * 42).toISOString(),
    minute: 42,
    lineups: {
      home: ["Raya", "White", "Saliba", "Gabriel", "Timber", "Odegaard", "Partey", "Rice", "Saka", "Havertz", "Martinelli"],
      away: ["Ederson", "Walker", "Dias", "Akanji", "Gvardiol", "Rodri", "Kovacic", "De Bruyne", "Foden", "Silva", "Haaland"]
    },
    timeline: [
      { time: 18, type: "Goal", detail: "Haaland (Assist: De Bruyne)", team: "away" },
      { time: 35, type: "Goal", detail: "Saka (Assist: Odegaard)", team: "home" }
    ],
    stats: {
      possession: { home: 45, away: 55 },
      shots: { home: 5, away: 8 },
      xG: { home: 0.8, away: 1.1 }
    },
    win_probability: { home: 33, draw: 35, away: 32 },
    ai_preview: "Chempionlik uchun kurashadigan ikki gigant to'qnashuvi. Arsenal o'z maydonida ochko yo'qotmaslikka harakat qiladi.",
    ai_analysis: ""
  },
  {
    id: 2003,
    league_id: 1000,
    league_name: "Uzbekistan Super League",
    home_team_name: "Pakhtakor",
    away_team_name: "Navbahor",
    home_team_logo: "https://upload.wikimedia.org/wikipedia/en/e/e0/Pakhtakor_Tashkent_FK.png",
    away_team_logo: "https://upload.wikimedia.org/wikipedia/uz/c/cf/Navbahor_namangan_logo.png",
    status: "LIVE",
    score_home: 0,
    score_away: 0,
    match_time: new Date(Date.now() - 60000 * 15).toISOString(),
    minute: 15,
    lineups: {
      home: ["Nazarov", "Saiyodv", "Alijonov", "Hamraliev", "Azmiddinov", "Sobirkhodjaev", "Kholmatov", "Hamdamov", "Ceran", "Adhamzoda", "Usmonov"],
      away: ["Yusupov", "Golban", "Ivanovic", "Milovic", "Sayfiev", "Ismailov", "Iskanderov", "Boltaboev", "Turgunboev", "Tabatadze", "Jahongirov"]
    },
    timeline: [],
    stats: {
      possession: { home: 50, away: 50 },
      shots: { home: 2, away: 1 },
      xG: { home: 0.15, away: 0.08 }
    },
    win_probability: { home: 40, draw: 35, away: 25 },
    ai_preview: "O'zbekiston derbisi deb ataluvchi ushbu bahsda murosasiz kurash kechishi kutilmoqda.",
    ai_analysis: ""
  }
];

export function getLocalMatches(): Match[] {
  if (typeof window === "undefined") return DEFAULT_MATCHES;
  const saved = localStorage.getItem("local_matches");
  if (!saved) {
    localStorage.setItem("local_matches", JSON.stringify(DEFAULT_MATCHES));
    return DEFAULT_MATCHES;
  }
  return JSON.parse(saved);
}

export function saveLocalMatches(matches: Match[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem("local_matches", JSON.stringify(matches));
}

export function getLocalNews(): NewsItem[] {
  if (typeof window === "undefined") return DEFAULT_NEWS;
  const saved = localStorage.getItem("local_news");
  if (!saved) {
    localStorage.setItem("local_news", JSON.stringify(DEFAULT_NEWS));
    return DEFAULT_NEWS;
  }
  return JSON.parse(saved);
}

export function saveLocalNews(news: NewsItem[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem("local_news", JSON.stringify(news));
}

export function simulateLocalTick() {
  const matches = getLocalMatches();
  const updated = matches.map(m => {
    if (m.status !== "LIVE") return m;
    const nextMinute = m.minute + 1;
    let nextStatus = m.status;
    if (nextMinute >= 90) {
      nextStatus = "FT";
      m.ai_analysis = "Murosasiz kechgan bahs yakunlandi. Har ikki jamoa ham g'alabaga loyiq o'yin ko'rsatdi.";
    }
    
    // Simulate score chance
    let scoreHome = m.score_home;
    let scoreAway = m.score_away;
    const timeline = [...(m.timeline || [])];
    const stats = m.stats ? { ...m.stats } : { possession: { home: 50, away: 50 }, shots: { home: 0, away: 0 }, xG: { home: 0, away: 0 } };
    
    if (Math.random() > 0.95 && nextStatus === "LIVE") {
      const isHome = Math.random() > 0.5;
      if (isHome) {
        scoreHome += 1;
        timeline.push({
          time: nextMinute,
          type: "Goal",
          detail: "Gooool! Mezbonlar to'p kiritdi!",
          team: "home"
        });
      } else {
        scoreAway += 1;
        timeline.push({
          time: nextMinute,
          type: "Goal",
          detail: "Gooool! Mehmonlar javob qaytardi!",
          team: "away"
        });
      }
    }
    
    // update stats randomly
    if (nextStatus === "LIVE") {
      stats.possession.home = Math.min(Math.max(stats.possession.home + (Math.random() > 0.5 ? 1 : -1), 30), 70);
      stats.possession.away = 100 - stats.possession.home;
      if (Math.random() > 0.8) stats.shots.home += 1;
      if (Math.random() > 0.8) stats.shots.away += 1;
      stats.xG.home = parseFloat((stats.xG.home + (Math.random() > 0.8 ? 0.1 : 0)).toFixed(2));
      stats.xG.away = parseFloat((stats.xG.away + (Math.random() > 0.8 ? 0.1 : 0)).toFixed(2));
    }
    
    // Recalc win prob
    const prob = { home: 33, draw: 34, away: 33 };
    const diff = scoreHome - scoreAway;
    if (diff > 0) {
      prob.home = 50 + diff * 15;
      prob.draw = Math.max(10, 30 - diff * 10);
      prob.away = 100 - prob.home - prob.draw;
    } else if (diff < 0) {
      prob.away = 50 + Math.abs(diff) * 15;
      prob.draw = Math.max(10, 30 - Math.abs(diff) * 10);
      prob.home = 100 - prob.away - prob.draw;
    }
    
    return {
      ...m,
      minute: nextMinute,
      status: nextStatus,
      score_home: scoreHome,
      score_away: scoreAway,
      timeline,
      stats,
      win_probability: prob
    };
  });
  saveLocalMatches(updated);
  return updated;
}
