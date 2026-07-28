"use client";

import Link from "next/link";
import Image from "next/image";
import { Sparkles, ChevronRight } from "lucide-react";
import type { Match } from "../lib/types";

export function SpotlightCard({ match }: { match: Match }) {
  return (
    <div className="xl:col-span-2 relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-slate-950 via-[#0a0f1d] to-[#04060d] p-6 md:p-8 spotlight-card flex flex-col justify-between min-h-[400px]">
      {/* Ambient Background glow blobs */}
      <div className="absolute top-0 right-0 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-0 left-0 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl" />

      {/* Header info */}
      <div className="relative z-10 flex items-center justify-between">
        <span className="text-xs font-extrabold tracking-wider bg-white/5 border border-white/5 text-slate-300 px-3 py-1 rounded-full uppercase">
          {match.league_name} • MARKAZIY O'YIN
        </span>

        {match.status === "LIVE" ? (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-black bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <span className="w-2 h-2 bg-rose-500 rounded-full live-ping" />
            <span>JONLI {match.minute}'</span>
          </span>
        ) : (
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            {match.status === "FT" ? "Tugadi" : "Kutilmoqda"}
          </span>
        )}
      </div>

      {/* Score & Team Crests */}
      <div className="relative z-10 grid grid-cols-3 items-center py-10 md:py-16 text-center">
        {/* Home */}
        <div className="flex flex-col items-center space-y-4">
          <div className="w-18 h-18 md:w-24 md:h-24 bg-white/5 border border-white/5 rounded-2xl flex items-center justify-center p-3 hover:scale-105 transition-transform">
            {match.home_team_logo ? (
              <Image
                src={match.home_team_logo}
                alt={match.home_team_name}
                width={72}
                height={72}
                className="w-full h-full object-contain"
                unoptimized
              />
            ) : (
              <span className="text-3xl font-black text-emerald-400">{match.home_team_name.substring(0, 2).toUpperCase()}</span>
            )}
          </div>
          <span className="text-sm md:text-lg font-bold tracking-tight">{match.home_team_name}</span>
        </div>

        {/* Score ticker */}
        <div className="flex flex-col items-center justify-center space-y-2">
          {match.status !== "NS" ? (
            <span className="text-4xl md:text-7xl font-black tracking-tighter bg-gradient-to-b from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
              {match.score_home} - {match.score_away}
            </span>
          ) : (
            <span className="text-slate-500 text-xs font-extrabold tracking-widest bg-white/5 px-4 py-1.5 rounded-full border border-white/5">VS</span>
          )}
          {match.status === "LIVE" && match.stats?.xG && (
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
              xG {match.stats.xG.home} - {match.stats.xG.away}
            </span>
          )}
        </div>

        {/* Away */}
        <div className="flex flex-col items-center space-y-4">
          <div className="w-18 h-18 md:w-24 md:h-24 bg-white/5 border border-white/5 rounded-2xl flex items-center justify-center p-3 hover:scale-105 transition-transform">
            {match.away_team_logo ? (
              <Image
                src={match.away_team_logo}
                alt={match.away_team_name}
                width={72}
                height={72}
                className="w-full h-full object-contain"
                unoptimized
              />
            ) : (
              <span className="text-3xl font-black text-cyan-400">{match.away_team_name.substring(0, 2).toUpperCase()}</span>
            )}
          </div>
          <span className="text-sm md:text-lg font-bold tracking-tight">{match.away_team_name}</span>
        </div>
      </div>

      {/* Ekspert Insights & Win Probability Footer */}
      <div className="relative z-10 pt-6 border-t border-white/5 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        <div className="flex-1 space-y-1.5">
          <div className="flex items-center text-xs font-extrabold text-emerald-400 uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 mr-1.5" />
            <span>Ekspert Tahlili</span>
          </div>
          <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
            {match.ai_preview || "Tahlil jarayoni boshlanmoqda..."}
          </p>
        </div>

        {match.win_probability && (
          <div className="md:w-64 space-y-1.5">
            <div className="flex justify-between text-[10px] font-extrabold text-slate-400 uppercase tracking-widest">
              <span>🏠 {match.win_probability.home}%</span>
              <span>🤝 {match.win_probability.draw}%</span>
              <span>✈️ {match.win_probability.away}%</span>
            </div>
            <div className="w-full h-1.5 rounded-full overflow-hidden flex bg-white/5 border border-white/5">
              <div className="h-full bg-emerald-500 transition-all duration-500" style={{ width: `${match.win_probability.home}%` }} />
              <div className="h-full bg-slate-500 transition-all duration-500" style={{ width: `${match.win_probability.draw}%` }} />
              <div className="h-full bg-cyan-500 transition-all duration-500" style={{ width: `${match.win_probability.away}%` }} />
            </div>
          </div>
        )}

        <Link
          href={`/matches/${match.id}`}
          className="bg-white text-slate-950 font-extrabold px-5 py-2.5 rounded-xl hover:bg-slate-200 transition-all flex items-center justify-center space-x-1.5 text-xs shadow-md shadow-white/5"
        >
          <span>O'yin Markazi</span>
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
