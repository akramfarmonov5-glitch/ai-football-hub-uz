"use client";

import Link from "next/link";
import Image from "next/image";
import { Sparkles } from "lucide-react";
import type { Match } from "../lib/types";
import { formatTime } from "../lib/time";
import { liveLabel } from "../lib/matchStatus";
import { MatchCountdown } from "./MatchCountdown";

export function MatchCard({ match, live = false, finished = false }: { match: Match; live?: boolean; finished?: boolean }) {
  const localTime = formatTime(match.match_time);

  return (
    <Link
      href={`/matches/${match.id}`}
      className={`block glass-panel rounded-2xl p-5 hover:scale-[1.01] transition-all duration-300 border ${
        live ? "border-rose-500/25 bg-rose-500/[0.02]" : "border-white/5"
      } relative overflow-hidden`}
    >
      {/* Top badges */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-[10px] font-bold text-slate-400 bg-white/5 border border-white/5 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
          {match.league_name}
        </span>

        {live ? (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-black bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <span className="w-1.5 h-1.5 bg-rose-500 rounded-full animate-ping" />
            <span>{liveLabel(match)}</span>
          </span>
        ) : finished ? (
          <span className="text-[9px] font-bold text-slate-500 bg-white/5 px-2 py-0.5 rounded uppercase tracking-wider">
            Tugadi
          </span>
        ) : (
          <span className="text-[9px] font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded uppercase tracking-wider">
            {localTime}
          </span>
        )}
      </div>

      {/* Teams Scoreboard */}
      <div className="flex items-center justify-between py-2 text-center">
        {/* Home */}
        <div className="flex flex-col items-center space-y-2 flex-1">
          <div className="w-12 h-12 bg-white/5 border border-white/5 rounded-xl flex items-center justify-center p-2">
            {match.home_team_logo ? (
              <Image
                src={match.home_team_logo}
                alt={match.home_team_name}
                width={32}
                height={32}
                className="w-full h-full object-contain"
                unoptimized
              />
            ) : (
              <span className="text-base font-black text-emerald-400">{match.home_team_name.substring(0, 2).toUpperCase()}</span>
            )}
          </div>
          <span className="text-xs font-extrabold text-slate-200 line-clamp-1">{match.home_team_name}</span>
        </div>

        {/* Score */}
        <div className="px-4">
          {!finished && match.status === "NS" ? (
            <span className="text-[10px] text-slate-500 font-black tracking-widest">VS</span>
          ) : (
            <span className="text-2xl font-black tracking-tighter bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
              {match.score_home} : {match.score_away}
            </span>
          )}
        </div>

        {/* Away */}
        <div className="flex flex-col items-center space-y-2 flex-1">
          <div className="w-12 h-12 bg-white/5 border border-white/5 rounded-xl flex items-center justify-center p-2">
            {match.away_team_logo ? (
              <Image
                src={match.away_team_logo}
                alt={match.away_team_name}
                width={32}
                height={32}
                className="w-full h-full object-contain"
                unoptimized
              />
            ) : (
              <span className="text-base font-black text-cyan-400">{match.away_team_name.substring(0, 2).toUpperCase()}</span>
            )}
          </div>
          <span className="text-xs font-extrabold text-slate-200 line-clamp-1">{match.away_team_name}</span>
        </div>
      </div>

      {/* Win probability bar */}
      {match.win_probability && (
        <div className="mt-4 pt-3 border-t border-white/5 space-y-1">
          <div className="flex items-center justify-between text-[9px] text-slate-500 font-bold uppercase tracking-wider">
            <span className="flex items-center"><Sparkles className="w-3 h-3 text-emerald-400 mr-1" /> G'alaba ehtimoli</span>
            <span>🏠 {match.win_probability.home}% · 🤝 {match.win_probability.draw}% · ✈️ {match.win_probability.away}%</span>
          </div>
          <div className="w-full h-1 rounded-full overflow-hidden flex bg-white/5">
            <div className="h-full bg-emerald-500" style={{ width: `${match.win_probability.home}%` }} />
            <div className="h-full bg-slate-600" style={{ width: `${match.win_probability.draw}%` }} />
            <div className="h-full bg-cyan-500" style={{ width: `${match.win_probability.away}%` }} />
          </div>
        </div>
      )}

      {/* Countdown timer for upcoming matches */}
      {!finished && !live && match.status === "NS" && (
        <MatchCountdown matchTime={match.match_time} />
      )}
    </Link>
  );
}
