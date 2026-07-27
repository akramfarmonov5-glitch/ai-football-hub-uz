"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { 
  ArrowLeft, 
  Sparkles, 
  Users, 
  BarChart2, 
  Clock, 
  ShieldAlert,
  Percent,
  CheckCircle2
} from "lucide-react";
import { getLocalMatches, Match } from "../../../lib/mockStore";
import { apiUrl, WS_URL } from "../../../lib/api";

export default function MatchDetail({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const matchId = resolvedParams.id;
  const [match, setMatch] = useState<Match | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"ai" | "lineup" | "stats" | "events">("ai");

  useEffect(() => {
    async function fetchMatch() {
      try {
        const res = await fetch(apiUrl(`/matches/${matchId}`));
        if (res.ok) {
          setMatch(await res.json());
        } else {
          throw new Error("Match API error status");
        }
      } catch (err) {
        console.warn("Backend offline, loading match from local mock store.");
        const matches = getLocalMatches();
        const found = matches.find(m => m.id === parseInt(matchId));
        if (found) setMatch(found);
      } finally {
        setLoading(false);
      }
    }
    fetchMatch();

    // WS Connection for real-time update in details page
    const socket = new WebSocket(WS_URL);
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.event === "match_update" && data.match.id === parseInt(matchId)) {
          setMatch((prev) => prev ? { ...prev, ...data.match } : null);
        }
      } catch (err) {
        console.error(err);
      }
    };

    // Client-side local updates checking (if offline)
    const clientSimulationInterval = setInterval(() => {
      if (socket.readyState !== WebSocket.OPEN) {
        const matches = getLocalMatches();
        const found = matches.find(m => m.id === parseInt(matchId));
        if (found) {
          setMatch(found);
        }
      }
    }, 3000);

    return () => {
      socket.close();
      clearInterval(clientSimulationInterval);
    };
  }, [matchId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <div className="w-8 h-8 border-4 border-emerald-400 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400">Match ma'lumotlari yuklanmoqda...</p>
      </div>
    );
  }

  if (!match) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-bold">O'yin topilmadi</h2>
        <Link href="/" className="text-emerald-400 inline-flex items-center mt-4">
          <ArrowLeft className="w-4 h-4 mr-2" /> Bosh sahifaga qaytish
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Back button */}
      <Link href="/" className="inline-flex items-center text-slate-400 hover:text-emerald-400 text-sm transition-colors">
        <ArrowLeft className="w-4 h-4 mr-2" /> Match markaziga qaytish
      </Link>

      {/* Main Scoreboard Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-[#0a1122] to-slate-900 border border-white/5 p-6 md:p-10">
        <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/5 rounded-full blur-3xl" />
        
        <div className="relative z-10 flex flex-col items-center text-center space-y-6">
          <span className="text-xs font-bold px-3 py-1 bg-white/5 border border-white/5 rounded-full text-slate-400">
            {match.league_name}
          </span>

          <div className="flex items-center justify-center space-x-6 md:space-x-12 w-full max-w-2xl">
            <div className="flex flex-col items-center space-y-3 flex-1">
              <div className="w-16 h-16 md:w-20 md:h-20 bg-emerald-500/5 rounded-full border border-white/5 flex items-center justify-center">
                {match.home_team_logo ? (
                  <img src={match.home_team_logo} alt={match.home_team_name} className="w-12 h-12 object-contain" />
                ) : (
                  <span className="text-2xl font-bold text-emerald-400">{match.home_team_name.substring(0, 2).toUpperCase()}</span>
                )}
              </div>
              <h2 className="text-base md:text-xl font-bold">{match.home_team_name}</h2>
            </div>

            <div className="flex flex-col items-center space-y-2">
              {match.status !== "NS" ? (
                <div className="text-4xl md:text-6xl font-black tracking-wider text-slate-100">
                  {match.score_home} - {match.score_away}
                </div>
              ) : (
                <div className="text-lg text-slate-500 font-bold">VS</div>
              )}
              
              {match.status === "LIVE" ? (
                <span className="inline-flex items-center space-x-1.5 px-3 py-0.5 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/25">
                  <span className="w-2 h-2 bg-rose-500 rounded-full animate-ping" />
                  <span>{match.minute}' Daqiqa</span>
                </span>
              ) : match.status === "FT" ? (
                <span className="text-xs bg-slate-500/10 text-slate-400 border border-slate-500/20 px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                  Tugadi
                </span>
              ) : (
                <span className="text-xs bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                  Boshlanmagan
                </span>
              )}
            </div>

            <div className="flex flex-col items-center space-y-3 flex-1">
              <div className="w-16 h-16 md:w-20 md:h-20 bg-cyan-500/5 rounded-full border border-white/5 flex items-center justify-center">
                {match.away_team_logo ? (
                  <img src={match.away_team_logo} alt={match.away_team_name} className="w-12 h-12 object-contain" />
                ) : (
                  <span className="text-2xl font-bold text-cyan-400">{match.away_team_name.substring(0, 2).toUpperCase()}</span>
                )}
              </div>
              <h2 className="text-base md:text-xl font-bold">{match.away_team_name}</h2>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-white/5 flex space-x-8 text-sm font-semibold">
        <button
          onClick={() => setActiveTab("ai")}
          className={`pb-4 transition-all flex items-center space-x-2 border-b-2 ${
            activeTab === "ai" ? "border-emerald-400 text-emerald-400" : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>AI Tahlillar & Prognoz</span>
        </button>
        <button
          onClick={() => setActiveTab("stats")}
          className={`pb-4 transition-all flex items-center space-x-2 border-b-2 ${
            activeTab === "stats" ? "border-emerald-400 text-emerald-400" : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <BarChart2 className="w-4 h-4" />
          <span>O'yin Statistikasi</span>
        </button>
        <button
          onClick={() => setActiveTab("lineup")}
          className={`pb-4 transition-all flex items-center space-x-2 border-b-2 ${
            activeTab === "lineup" ? "border-emerald-400 text-emerald-400" : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Tarkiblar</span>
        </button>
        <button
          onClick={() => setActiveTab("events")}
          className={`pb-4 transition-all flex items-center space-x-2 border-b-2 ${
            activeTab === "events" ? "border-emerald-400 text-emerald-400" : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Clock className="w-4 h-4" />
          <span>O'yin Voqealari</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-6">
          {activeTab === "ai" && (
            <div className="space-y-6">
              {match.win_probability && (
                <div className="glass-panel p-6 rounded-2xl space-y-4">
                  <h3 className="text-base font-bold flex items-center text-cyan-400">
                    <Percent className="w-4 h-4 mr-2" /> G'alaba qozonish ehtimoli (AI)
                  </h3>
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs font-semibold text-slate-300">
                      <span>{match.home_team_name} ({match.win_probability.home}%)</span>
                      <span>Durang ({match.win_probability.draw}%)</span>
                      <span>{match.away_team_name} ({match.win_probability.away}%)</span>
                    </div>
                    <div className="w-full h-3 rounded-full overflow-hidden flex bg-white/5 border border-white/5">
                      <div className="h-full bg-emerald-500 transition-all duration-500" style={{ width: `${match.win_probability.home}%` }} />
                      <div className="h-full bg-slate-500 transition-all duration-500" style={{ width: `${match.win_probability.draw}%` }} />
                      <div className="h-full bg-cyan-500 transition-all duration-500" style={{ width: `${match.win_probability.away}%` }} />
                    </div>
                  </div>
                </div>
              )}

              <div className="glass-panel p-6 rounded-2xl space-y-4">
                <h3 className="text-base font-bold flex items-center text-emerald-400">
                  <Sparkles className="w-4 h-4 mr-2" /> AI O'yinoldi Preview
                </h3>
                <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-line bg-slate-950/20 p-4 rounded-xl border border-white/5">
                  {match.ai_preview || "Tahlil tayyorlanmoqda..."}
                </div>
              </div>

              {match.status === "FT" && (
                <div className="glass-panel p-6 rounded-2xl space-y-4 border border-emerald-500/20">
                  <h3 className="text-base font-bold flex items-center text-teal-400">
                    <CheckCircle2 className="w-4 h-4 mr-2" /> Post-Match AI Ekspert Tahlili
                  </h3>
                  <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-line bg-slate-950/20 p-4 rounded-xl border border-white/5">
                    {match.ai_analysis || "O'yin yakunlandi. AI tahlilini yuklash kutilmoqda."}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === "stats" && (
            <div className="glass-panel p-6 rounded-2xl space-y-6">
              <h3 className="text-base font-bold">Uchrashuv statistikasi</h3>
              {match.stats ? (
                <div className="space-y-6">
                  <StatBar 
                    label="To'p nazorati (%)" 
                    homeVal={match.stats.possession.home} 
                    awayVal={match.stats.possession.away} 
                  />
                  <StatBar 
                    label="Zarbalar (Umumiy)" 
                    homeVal={match.stats.shots.home} 
                    awayVal={match.stats.shots.away} 
                  />
                  <StatBar 
                    label="Kutilayotgan gollar (xG)" 
                    homeVal={match.stats.xG.home} 
                    awayVal={match.stats.xG.away} 
                    float
                  />
                </div>
              ) : (
                <p className="text-sm text-slate-500 text-center py-6">Statistikalar faqat o'yin boshlangach ko'rinadi.</p>
              )}
            </div>
          )}

          {activeTab === "lineup" && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="glass-panel p-5 rounded-2xl space-y-4">
                <h3 className="font-bold text-emerald-400 text-sm border-b border-white/5 pb-2">{match.home_team_name}</h3>
                {match.lineups?.home ? (
                   <ul className="text-xs space-y-2.5 text-slate-300">
                     {match.lineups.home.map((p, idx) => (
                       <li key={p} className="flex items-center space-x-2">
                         <span className="w-5 h-5 bg-white/5 text-slate-400 flex items-center justify-center rounded-full text-[10px]">{idx + 1}</span>
                         <span>{p}</span>
                       </li>
                     ))}
                   </ul>
                ) : (
                  <p className="text-xs text-slate-500">Tarkiblar e'lon qilinmagan.</p>
                )}
              </div>

              <div className="glass-panel p-5 rounded-2xl space-y-4">
                <h3 className="font-bold text-cyan-400 text-sm border-b border-white/5 pb-2">{match.away_team_name}</h3>
                {match.lineups?.away ? (
                   <ul className="text-xs space-y-2.5 text-slate-300">
                     {match.lineups.away.map((p, idx) => (
                       <li key={p} className="flex items-center space-x-2">
                         <span className="w-5 h-5 bg-white/5 text-slate-400 flex items-center justify-center rounded-full text-[10px]">{idx + 1}</span>
                         <span>{p}</span>
                       </li>
                     ))}
                   </ul>
                ) : (
                  <p className="text-xs text-slate-500">Tarkiblar e'lon qilinmagan.</p>
                )}
              </div>
            </div>
          )}

          {activeTab === "events" && (
            <div className="glass-panel p-6 rounded-2xl space-y-6">
              <h3 className="text-base font-bold">O'yin xronologiyasi (Timeline)</h3>
              {match.timeline && match.timeline.length > 0 ? (
                <div className="relative border-l border-white/5 ml-4 pl-6 space-y-6">
                  {match.timeline.map((event, idx) => (
                    <div key={idx} className="relative">
                      <span className={`absolute -left-[31px] top-0 w-4 h-4 rounded-full border-2 border-slate-900 flex items-center justify-center text-[10px] font-bold ${
                         event.type === "Goal" ? "bg-emerald-400 text-slate-950" : "bg-yellow-400 text-slate-950"
                      }`}>
                        {event.time}'
                      </span>
                      <div className="space-y-1">
                        <span className="text-xs text-slate-400 uppercase font-semibold">
                          {event.type === "Goal" ? "⚽ Gol!" : "🟨 Ogohlantirish"}
                        </span>
                        <p className="text-sm font-semibold text-slate-200">{event.detail}</p>
                        <p className="text-xs text-slate-500">
                          Jamoa: {event.team === "home" ? match.home_team_name : match.away_team_name}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500 text-center py-6">Hozircha hech qanday hodisa ro'y bermadi.</p>
              )}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="glass-panel p-5 rounded-2xl space-y-4">
            <h4 className="font-bold text-sm">O'yin haqida ma'lumot</h4>
            <div className="space-y-3 text-xs text-slate-400">
              <div className="flex justify-between">
                <span>Liga:</span>
                <span className="font-semibold text-slate-200">{match.league_name}</span>
              </div>
              <div className="flex justify-between">
                <span>Sana:</span>
                <span className="font-semibold text-slate-200">
                  {new Date(match.match_time).toLocaleDateString("uz-UZ")}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Vaqt:</span>
                <span className="font-semibold text-slate-200">
                  {new Date(match.match_time).toLocaleTimeString("uz-UZ", { hour: "2-digit", minute: "2-digit" })}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Status:</span>
                <span className="font-semibold text-slate-200 uppercase">{match.status}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatBar({ label, homeVal, awayVal, float = false }: { label: string; homeVal: number; awayVal: number; float?: boolean }) {
  const total = homeVal + awayVal;
  const homePct = total > 0 ? (homeVal / total) * 100 : 50;
  
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs text-slate-300">
        <span>{float ? homeVal.toFixed(2) : homeVal}</span>
        <span className="text-slate-400 font-semibold">{label}</span>
        <span>{float ? awayVal.toFixed(2) : awayVal}</span>
      </div>
      <div className="w-full h-2 rounded-full overflow-hidden flex bg-white/5">
        <div className="h-full bg-emerald-500" style={{ width: `${homePct}%` }} />
        <div className="h-full bg-cyan-500" style={{ width: `${100 - homePct}%` }} />
      </div>
    </div>
  );
}
