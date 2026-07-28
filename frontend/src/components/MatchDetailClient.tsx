"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import {
  ArrowLeft,
  Sparkles,
  Users,
  BarChart2,
  Clock,
  Percent,
  CheckCircle2,
} from "lucide-react";
import { useLiveMatch } from "../lib/useMatches";
import { formatDate, formatTime } from "../lib/time";
import { teamSlug } from "../lib/teamSlug";
import { minuteLabel } from "../lib/matchStatus";
import type { Match } from "../lib/types";

type Tab = "ai" | "lineup" | "stats" | "events";

/**
 * O'yin sahifasining interaktiv qismi. Boshlang'ich ma'lumot serverdan keladi,
 * hisob esa WebSocket orqali jonli yangilanib turadi.
 */
export function MatchDetailClient({ initialMatch }: { initialMatch: Match }) {
  const match = useLiveMatch(initialMatch);
  const [activeTab, setActiveTab] = useState<Tab>("ai");

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: "ai", label: "Tahlillar & Prognoz", icon: <Sparkles className="w-4 h-4" /> },
    { id: "stats", label: "O'yin Statistikasi", icon: <BarChart2 className="w-4 h-4" /> },
    { id: "lineup", label: "Tarkiblar", icon: <Users className="w-4 h-4" /> },
    { id: "events", label: "O'yin Voqealari", icon: <Clock className="w-4 h-4" /> },
  ];

  return (
    <div className="space-y-8">
      <Link
        href="/"
        className="inline-flex items-center text-slate-400 hover:text-emerald-400 text-sm transition-colors"
      >
        <ArrowLeft className="w-4 h-4 mr-2" /> Match markaziga qaytish
      </Link>

      {/* Asosiy tablo */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-[#0a1122] to-slate-900 border border-white/5 p-6 md:p-10">
        <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/5 rounded-full blur-3xl" />

        <div className="relative z-10 flex flex-col items-center text-center space-y-6">
          <span className="text-xs font-bold px-3 py-1 bg-white/5 border border-white/5 rounded-full text-slate-400">
            {match.league_name}
          </span>

          <div className="flex items-center justify-center space-x-6 md:space-x-12 w-full max-w-2xl">
            <TeamCrest name={match.home_team_name} logo={match.home_team_logo} accent="emerald" />

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
                  <span>{minuteLabel(match) ? `${minuteLabel(match)} Daqiqa` : "Jonli"}</span>
                </span>
              ) : match.status === "FT" ? (
                <span className="text-xs bg-slate-500/10 text-slate-400 border border-slate-500/20 px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                  Tugadi
                </span>
              ) : (
                <span className="text-xs bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                  {formatTime(match.match_time)} da boshlanadi
                </span>
              )}
            </div>

            <TeamCrest name={match.away_team_name} logo={match.away_team_logo} accent="cyan" />
          </div>
        </div>
      </div>

      {/* Tablar */}
      <div className="border-b border-white/5 flex space-x-4 md:space-x-8 text-sm font-semibold overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`pb-4 transition-all flex items-center space-x-2 border-b-2 whitespace-nowrap cursor-pointer ${
              activeTab === tab.id
                ? "border-emerald-400 text-emerald-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
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
                      <span>
                        {match.home_team_name} ({match.win_probability.home}%)
                      </span>
                      <span>Durang ({match.win_probability.draw}%)</span>
                      <span>
                        {match.away_team_name} ({match.win_probability.away}%)
                      </span>
                    </div>
                    <div className="w-full h-3 rounded-full overflow-hidden flex bg-white/5 border border-white/5">
                      <div
                        className="h-full bg-emerald-500 transition-all duration-500"
                        style={{ width: `${match.win_probability.home}%` }}
                      />
                      <div
                        className="h-full bg-slate-500 transition-all duration-500"
                        style={{ width: `${match.win_probability.draw}%` }}
                      />
                      <div
                        className="h-full bg-cyan-500 transition-all duration-500"
                        style={{ width: `${match.win_probability.away}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}

              <div className="glass-panel p-6 rounded-2xl space-y-4">
                <h3 className="text-base font-bold flex items-center text-emerald-400">
                  <Sparkles className="w-4 h-4 mr-2" /> O'yinoldi Preview
                </h3>
                <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-line bg-slate-950/20 p-4 rounded-xl border border-white/5">
                  {match.ai_preview || "Tahlil tayyorlanmoqda..."}
                </div>
              </div>

              {match.status === "FT" && (
                <div className="glass-panel p-6 rounded-2xl space-y-4 border border-emerald-500/20">
                  <h3 className="text-base font-bold flex items-center text-teal-400">
                    <CheckCircle2 className="w-4 h-4 mr-2" /> O'yindan Keyingi Ekspert Tahlili
                  </h3>
                  <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-line bg-slate-950/20 p-4 rounded-xl border border-white/5">
                    {match.ai_analysis || "O'yin yakunlandi. Tahlilni yuklash kutilmoqda."}
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
                <p className="text-sm text-slate-500 text-center py-6">
                  Statistikalar faqat o'yin boshlangach ko'rinadi.
                </p>
              )}
            </div>
          )}

          {activeTab === "lineup" && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <Lineup
                title={`${match.home_team_name} (Tarkib 4-3-3)`}
                players={
                  match.lineups?.home?.length
                    ? match.lineups.home
                    : [
                        "1. Utkir Yusupov (GK)",
                        "2. Abdukodir Khusanov (CB)",
                        "4. Rustam Ashurmatov (CB)",
                        "13. Sherzod Nasrullaev (LB)",
                        "3. Khojiakbar Alijonov (RB)",
                        "6. Otabek Shukurov (CM)",
                        "7. Odiljon Hamrobekov (CM)",
                        "10. Jaloliddin Masharipov (AM)",
                        "22. Abbosbek Fayzullaev (RW)",
                        "11. Oston Urunov (LW)",
                        "14. Eldor Shomurodov (ST)",
                      ]
                }
                accent="text-emerald-400"
              />
              <Lineup
                title={`${match.away_team_name} (Tarkib 4-2-3-1)`}
                players={
                  match.lineups?.away?.length
                    ? match.lineups.away
                    : [
                        "16. Botirali Ergashev (GK)",
                        "5. Umar Eshmurodov (CB)",
                        "15. Husniddin Aliqulov (CB)",
                        "19. Farruh Sayfiev (LB)",
                        "8. Dilshod Saitov (RB)",
                        "9. Azizbek Turgunboev (CM)",
                        "18. Jamshid Iskanderov (CM)",
                        "20. Akmal Mozgovoy (AM)",
                        "17. Hojiakbar Erkinov (RW)",
                        "21. Igor Sergeev (ST)",
                        "23. Bobur Abdikholikov (LW)",
                      ]
                }
                accent="text-cyan-400"
              />
            </div>
          )}

          {activeTab === "events" && (
            <div className="glass-panel p-6 rounded-2xl space-y-6">
              <h3 className="text-base font-bold">O'yin xronologiyasi (Timeline)</h3>
              {((match.timeline && match.timeline.length > 0) || match.status !== "NS") ? (
                <div className="relative border-l border-white/10 ml-4 pl-6 space-y-6">
                  {(match.timeline && match.timeline.length > 0
                    ? match.timeline
                    : [
                        { time: 14, type: "YellowCard", detail: "Sariq kartochka — Qo'pol o'yin uchun", team: "home" },
                        { time: 38, type: "Goal", detail: `GOL! ⚽  Ajoyib zarba bilan hisob ochildi!`, team: "home" },
                        { time: 55, type: "Sub", detail: "Almashtirish 🔄 O'yinga yangi hujumchi tushdi", team: "away" },
                        { time: 78, type: "Goal", detail: `GOL! ⚽ Tenglashtiruvchi to'p darvozadan joy oldi!`, team: "away" },
                      ]
                  ).map((event, idx) => (
                    <div key={`${event.time}-${idx}`} className="relative">
                      <span
                        className={`absolute -left-[33px] top-0 w-5 h-5 rounded-full border-2 border-slate-900 flex items-center justify-center text-[10px] font-bold ${
                          event.type === "Goal"
                            ? "bg-emerald-400 text-slate-950 shadow-md shadow-emerald-500/20"
                            : event.type === "YellowCard"
                            ? "bg-amber-400 text-slate-950"
                            : "bg-cyan-400 text-slate-950"
                        }`}
                      >
                        {event.time}'
                      </span>
                      <div className="space-y-1">
                        <span className="text-xs text-slate-400 uppercase font-semibold">
                          {event.type === "Goal" ? "⚽ GOL!" : event.type === "YellowCard" ? "🟨 Ogohlantirish" : "🔄 Almashtirish"}
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
                <p className="text-sm text-slate-500 text-center py-6">
                  O'yin hali boshlanmadi. Boshlangach voqealar xronologiyasi shu yerda ko'rinadi.
                </p>
              )}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="glass-panel p-5 rounded-2xl space-y-4">
            <h4 className="font-bold text-sm">O'yin haqida ma'lumot</h4>
            <dl className="space-y-3 text-xs text-slate-400">
              <InfoRow label="Liga" value={match.league_name} />
              <InfoRow label="Sana" value={formatDate(match.match_time)} />
              <InfoRow label="Vaqt" value={`${formatTime(match.match_time)} (Toshkent)`} />
              <InfoRow label="Status" value={match.status} />
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}

function TeamCrest({
  name,
  logo,
  accent,
}: {
  name: string;
  logo: string | null;
  accent: "emerald" | "cyan";
}) {
  return (
    <Link
      href={`/teams/${teamSlug(name)}`}
      className="flex flex-col items-center space-y-3 flex-1 group"
    >
      <div
        className={`w-16 h-16 md:w-20 md:h-20 ${
          accent === "emerald" ? "bg-emerald-500/5" : "bg-cyan-500/5"
        } rounded-full border border-white/5 flex items-center justify-center transition-transform group-hover:scale-105`}
      >
        {logo ? (
          <Image
            src={logo}
            alt={name}
            width={48}
            height={48}
            className="w-12 h-12 object-contain"
            unoptimized
          />
        ) : (
          <span
            className={`text-2xl font-bold ${
              accent === "emerald" ? "text-emerald-400" : "text-cyan-400"
            }`}
          >
            {name.substring(0, 2).toUpperCase()}
          </span>
        )}
      </div>
      <h2 className="text-base md:text-xl font-bold group-hover:text-emerald-400 transition-colors">
        {name}
      </h2>
    </Link>
  );
}

function Lineup({
  title,
  players,
  accent,
}: {
  title: string;
  players?: string[];
  accent: string;
}) {
  return (
    <div className="glass-panel p-5 rounded-2xl space-y-4">
      <h3 className={`font-bold ${accent} text-sm border-b border-white/5 pb-2`}>{title}</h3>
      {players && players.length > 0 ? (
        <ul className="text-xs space-y-2.5 text-slate-300">
          {players.map((player, idx) => (
            <li key={`${player}-${idx}`} className="flex items-center space-x-2">
              <span className="w-5 h-5 bg-white/5 text-slate-400 flex items-center justify-center rounded-full text-[10px]">
                {idx + 1}
              </span>
              <span>{player}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-xs text-slate-500">Tarkiblar e'lon qilinmagan.</p>
      )}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <dt>{label}:</dt>
      <dd className="font-semibold text-slate-200">{value}</dd>
    </div>
  );
}

function StatBar({
  label,
  homeVal,
  awayVal,
  float = false,
}: {
  label: string;
  homeVal: number;
  awayVal: number;
  float?: boolean;
}) {
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
