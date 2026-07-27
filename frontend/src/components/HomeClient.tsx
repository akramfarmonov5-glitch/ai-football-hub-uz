"use client";

import { useState } from "react";
import Link from "next/link";
import { Tv, Sparkles, ArrowUpRight } from "lucide-react";
import { useMatches } from "../lib/useMatches";
import { SpotlightCard } from "./SpotlightCard";
import { NewsList } from "./NewsList";
import { MatchCard } from "./MatchCard";
import type { Match, NewsItem } from "../lib/types";

/**
 * Bosh sahifaning interaktiv qismi.
 *
 * Ma'lumot serverda yuklanadi va shu yerga `initial*` orqali uzatiladi —
 * shu sababli sahifa HTML'i to'liq kontent bilan keladi (Google va Telegram
 * uni ko'ra oladi), keyin WebSocket jonli yangilanishlarni ustiga qo'yadi.
 */
export function HomeClient({
  initialMatches,
  initialNews,
}: {
  initialMatches: Match[];
  initialNews: NewsItem[];
}) {
  const { matches, news, isOffline } = useMatches({ initialMatches, initialNews });
  const [selectedLeague, setSelectedLeague] = useState<string>("All");

  const leagues = ["All", ...Array.from(new Set(matches.map((m) => m.league_name)))];
  const filteredMatches =
    selectedLeague === "All"
      ? matches
      : matches.filter((m) => m.league_name === selectedLeague);

  const liveMatches = filteredMatches.filter((m) => m.status === "LIVE");
  const upcomingMatches = filteredMatches.filter((m) => m.status === "NS");
  const finishedMatches = filteredMatches.filter((m) => m.status === "FT");

  // Spotlight uchun: avval jonli, keyin bo'lajak, oxirida tugagan o'yin
  const spotlightMatch = liveMatches[0] || upcomingMatches[0] || finishedMatches[0];

  return (
    <div className="space-y-12">
      {isOffline && (
        <div className="flex items-center justify-between px-6 py-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/25 text-cyan-400 text-xs font-semibold shadow-lg">
          <span className="flex items-center">
            <Sparkles className="w-4 h-4 mr-2 text-cyan-300 animate-pulse" />
            Interaktiv Demo Rejimi Faol: Haqiqiy o'yinlar simulyatsiya qilinmoqda.
          </span>
          <Link href="/admin" className="underline hover:text-cyan-300 flex items-center">
            Simulyatorga o'tish <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
          </Link>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {spotlightMatch && <SpotlightCard match={spotlightMatch} />}
        <NewsList news={news} />
      </div>

      <div id="match-center" className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-white/5 pb-4 gap-4">
          <div className="flex items-center space-x-2">
            <Tv className="w-5 h-5 text-emerald-400" />
            <h2 className="text-xl font-bold">O'yin Markazi</h2>
          </div>

          <div className="flex items-center space-x-2 overflow-x-auto py-1 scrollbar-none">
            {leagues.map((league) => (
              <button
                key={league}
                onClick={() => setSelectedLeague(league)}
                className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all border whitespace-nowrap cursor-pointer ${
                  selectedLeague === league
                    ? "bg-gradient-to-r from-emerald-400 to-cyan-400 border-transparent text-slate-950 font-black shadow-md shadow-emerald-500/10"
                    : "bg-white/5 border-white/5 text-slate-400 hover:bg-white/10"
                }`}
              >
                {league === "All" ? "Barchasi" : league}
              </button>
            ))}
          </div>
        </div>

        {filteredMatches.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-12">
            Hozircha o'yinlar yo'q. Tez orada jadval to'ldiriladi.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {liveMatches.map((m) => (
              <MatchCard key={m.id} match={m} live />
            ))}
            {upcomingMatches.map((m) => (
              <MatchCard key={m.id} match={m} />
            ))}
            {finishedMatches.map((m) => (
              <MatchCard key={m.id} match={m} finished />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
