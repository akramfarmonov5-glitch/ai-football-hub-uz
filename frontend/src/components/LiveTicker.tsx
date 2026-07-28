"use client";

import Link from "next/link";
import { useMatches } from "../lib/useMatches";
import { getLocalMatches } from "../lib/mockStore";
import type { Match } from "../lib/types";
import { minuteLabel } from "../lib/matchStatus";

export function LiveTicker({ initialMatches }: { initialMatches: Match[] }) {
  const { matches } = useMatches({ initialMatches, initialNews: [] });

  const effectiveMatches = matches.length > 0 ? matches : getLocalMatches();
  const liveAndRecent = effectiveMatches.filter(
    (m) => m.status === "LIVE" || m.status === "FT"
  );

  if (liveAndRecent.length === 0) return null;

  // Ikki marta takrorlaymiz — uzluksiz sirpanish uchun
  const doubled = [...liveAndRecent, ...liveAndRecent];

  return (
    <div className="w-full bg-[#04060d] border-b border-white/5 overflow-hidden">
      <div className="max-w-7xl mx-auto relative">
        <div className="flex items-center">
          {/* Fixed label */}
          <div className="shrink-0 bg-rose-500/10 border-r border-white/5 px-3 py-2 z-10">
            <span className="flex items-center text-[10px] font-black text-rose-400 uppercase tracking-wider whitespace-nowrap">
              <span className="w-1.5 h-1.5 bg-rose-500 rounded-full animate-pulse mr-1.5" />
              JONLI
            </span>
          </div>

          {/* Scrolling ticker */}
          <div className="overflow-hidden flex-1">
            <div className="flex items-center animate-ticker whitespace-nowrap">
              {doubled.map((m, idx) => (
                <Link
                  key={`${m.id}-${idx}`}
                  href={`/matches/${m.id}`}
                  className="inline-flex items-center space-x-2 px-4 py-2 text-[11px] font-semibold text-slate-300 hover:text-emerald-400 transition-colors shrink-0"
                >
                  <span className="text-slate-400">{m.home_team_name}</span>
                  <span className={`font-black ${m.status === "LIVE" ? "text-emerald-400" : "text-slate-200"}`}>
                    {m.score_home} - {m.score_away}
                  </span>
                  <span className="text-slate-400">{m.away_team_name}</span>
                  {m.status === "LIVE" && minuteLabel(m) && (
                    <span className="text-[9px] text-rose-400 font-bold bg-rose-500/10 px-1.5 py-0.5 rounded">
                      {minuteLabel(m)}
                    </span>
                  )}
                  {m.status === "FT" && (
                    <span className="text-[9px] text-slate-500 font-bold">TUG</span>
                  )}
                  <span className="text-slate-700 ml-2">|</span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
