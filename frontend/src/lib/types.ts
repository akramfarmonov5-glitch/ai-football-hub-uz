/** Backend javoblarining shakli. Server va klient komponentlar bir xil turdan
 *  foydalanishi uchun alohida faylga ajratilgan (mockStore brauzerga bog'liq). */

export interface MatchStats {
  possession: { home: number; away: number };
  shots: { home: number; away: number };
  xG: { home: number; away: number };
}

export interface TimelineEvent {
  time: number;
  type: string;
  detail: string;
  team: string;
}

export interface Match {
  id: number;
  league_id: number;
  league_name: string;
  home_team_name: string;
  away_team_name: string;
  home_team_logo: string | null;
  away_team_logo: string | null;
  status: string;
  score_home: number;
  score_away: number;
  match_time: string;
  minute: number;
  lineups?: { home: string[]; away: string[] };
  timeline?: TimelineEvent[];
  stats?: MatchStats;
  ai_preview?: string;
  ai_analysis?: string;
  win_probability?: { home: number; draw: number; away: number };
}

export interface SiteMeta {
  data_source: "api-football" | "simulation";
  /** Rost bo'lsa — o'yinlar va natijalar to'qib chiqarilgan, haqiqiy emas */
  is_simulated: boolean;
  ai_enabled: boolean;
}

export type FormResult = "W" | "D" | "L";

export interface TeamStanding {
  position: number;
  team: string;
  logo: string | null;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
  /** Oxirgi 5 o'yin, eng yangisi oxirida */
  form: FormResult[];
}

export interface LeagueStandings {
  league_id: number;
  league_name: string;
  table: TeamStanding[];
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
