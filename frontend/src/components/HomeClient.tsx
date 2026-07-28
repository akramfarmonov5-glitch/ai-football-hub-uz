"use client";

import { useState } from "react";
import Link from "next/link";
import { Tv, Sparkles, ArrowUpRight, Zap, TrendingUp, Users } from "lucide-react";
import { useMatches } from "../lib/useMatches";
import { getLocalMatches, getLocalNews } from "../lib/mockStore";
import { SpotlightCard } from "./SpotlightCard";
import { NewsList } from "./NewsList";
import { MatchCard } from "./MatchCard";
import type { Match, NewsItem } from "../lib/types";

/**
 * Bosh sahifaning interaktiv qismi.
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

  const effectiveMatches = matches.length > 0 ? matches : getLocalMatches();
  const effectiveNews = news.length > 0 ? news : getLocalNews();

  const leagues = ["All", ...Array.from(new Set(effectiveMatches.map((m) => m.league_name)))];
  const filteredMatches =
    selectedLeague === "All"
      ? effectiveMatches
      : effectiveMatches.filter((m) => m.league_name === selectedLeague);

  const liveMatches = filteredMatches.filter((m) => m.status === "LIVE");
  const upcomingMatches = filteredMatches.filter((m) => m.status === "NS");
  const finishedMatches = filteredMatches.filter((m) => m.status === "FT");

  const spotlightMatch = liveMatches[0] || upcomingMatches[0] || finishedMatches[0] || effectiveMatches[0];

  return (
    <div className="space-y-12">
      {/* ===== Hero Banner ===== */}
      <section className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-[#0a1628] via-[#0d1f3c] to-[#060913] p-8 md:p-12 animate-fadeInUp">
        {/* Ambient glow blobs */}
        <div className="absolute top-0 left-0 w-80 h-80 bg-emerald-500/15 rounded-full blur-[100px] -translate-x-1/2 -translate-y-1/2" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-[120px] translate-x-1/3 translate-y-1/3" />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-purple-500/8 rounded-full blur-[80px] -translate-x-1/2 -translate-y-1/2" />

        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="flex-1 space-y-5 text-center md:text-left">
            <div className="inline-flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-4 py-1.5 rounded-full text-xs font-bold">
              <Zap className="w-3.5 h-3.5" />
              <span>O'zbekistondagi Birinchi AI Futbol Platformasi</span>
            </div>

            <h1 className="text-3xl md:text-5xl font-black tracking-tight leading-tight">
              <span className="bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
                Futbolni{" "}
              </span>
              <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                Sun'iy Intellekt
              </span>
              <br />
              <span className="bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
                bilan Kuzating
              </span>
            </h1>

            <p className="text-sm md:text-base text-slate-400 max-w-lg leading-relaxed">
              Jonli natijalar, real vaqtdagi statistikalar, AI prognozlari va O'zbekiston
              futboli yangiliklari — barchasi bir joyda.
            </p>

            <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
              <a
                href="#match-center"
                className="bg-gradient-to-r from-emerald-500 to-cyan-500 text-slate-950 font-extrabold px-6 py-3 rounded-xl hover:opacity-90 transition-opacity text-sm shadow-lg shadow-emerald-500/20 flex items-center space-x-2"
              >
                <Tv className="w-4 h-4" />
                <span>O'yinlarni ko'rish</span>
              </a>
              <a
                href="https://t.me/aifootball_uz"
                target="_blank"
                rel="noreferrer"
                className="bg-white/5 border border-white/10 text-slate-300 font-bold px-6 py-3 rounded-xl hover:bg-white/10 transition-all text-sm flex items-center space-x-2"
              >
                <span>📢 Telegram Kanal</span>
              </a>
            </div>
          </div>

          {/* Stats cards */}
          <div className="flex flex-row md:flex-col gap-4">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 text-center space-y-1 min-w-[100px]">
              <TrendingUp className="w-5 h-5 text-emerald-400 mx-auto" />
              <div className="text-2xl font-black text-white">{effectiveMatches.length}</div>
              <div className="text-[10px] text-slate-400 font-bold uppercase">O'yinlar</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 text-center space-y-1 min-w-[100px]">
              <Sparkles className="w-5 h-5 text-cyan-400 mx-auto" />
              <div className="text-2xl font-black text-white">{effectiveNews.length}</div>
              <div className="text-[10px] text-slate-400 font-bold uppercase">Yangilik</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 text-center space-y-1 min-w-[100px]">
              <Users className="w-5 h-5 text-purple-400 mx-auto" />
              <div className="text-2xl font-black text-white">{leagues.length - 1}</div>
              <div className="text-[10px] text-slate-400 font-bold uppercase">Ligalar</div>
            </div>
          </div>
        </div>
      </section>

      {/* Server ulanmasa ogohlantirish */}
      {isOffline && (
        <div className="flex items-center justify-between px-6 py-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/25 text-cyan-400 text-xs font-semibold shadow-lg animate-fadeInUp">
          <span className="flex items-center">
            <Sparkles className="w-4 h-4 mr-2 text-cyan-300 animate-pulse" />
            Serverga ulanib bo'lmadi — brauzerdagi zaxira ma'lumotlar ko'rsatilmoqda.
          </span>
          <Link href="/admin" className="underline hover:text-cyan-300 flex items-center">
            Simulyatorga o'tish <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
          </Link>
        </div>
      )}

      {/* Spotlight + News */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 animate-fadeInUp" style={{ animationDelay: "0.15s" }}>
        {spotlightMatch && <SpotlightCard match={spotlightMatch} />}
        <NewsList news={effectiveNews} />
      </div>

      {/* Match Center */}
      <div id="match-center" className="space-y-6 animate-fadeInUp" style={{ animationDelay: "0.25s" }}>
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 stagger-children">
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
