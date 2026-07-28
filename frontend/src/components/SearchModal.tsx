"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Search, X, Trophy, Shield, Newspaper, Calendar } from "lucide-react";
import type { Match, NewsItem, TeamSummary } from "../lib/types";
import { teamSlug } from "../lib/teamSlug";

export function SearchModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [matches, setMatches] = useState<Match[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [teams, setTeams] = useState<TeamSummary[]>([]);
  const [loading, setLoading] = useState(false);

  // Keyboard shortcut: Ctrl + K or Cmd + K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Fetch search data when modal opens
  useEffect(() => {
    if (!isOpen) return;
    const loadData = async () => {
      setLoading(true);
      try {
        const api = process.env.NEXT_PUBLIC_API_URL || "https://futbol-backend-ewbc.onrender.com";
        const [mRes, nRes, tRes] = await Promise.all([
          fetch(`${api}/api/v1/matches/`).then((r) => r.json()),
          fetch(`${api}/api/v1/news/`).then((r) => r.json()),
          fetch(`${api}/api/v1/teams/`).then((r) => r.json()),
        ]);
        if (Array.isArray(mRes)) setMatches(mRes);
        if (Array.isArray(nRes)) setNews(nRes);
        if (Array.isArray(tRes)) setTeams(tRes);
      } catch (err) {
        console.error("Qidiruv ma'lumotlarini yuklashda xato:", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [isOpen]);

  const q = query.trim().toLowerCase();

  const filteredMatches = q
    ? matches.filter(
        (m) =>
          m.home_team_name.toLowerCase().includes(q) ||
          m.away_team_name.toLowerCase().includes(q) ||
          m.league_name.toLowerCase().includes(q)
      ).slice(0, 5)
    : [];

  const filteredTeams = q
    ? teams.filter(
        (t) => t.name.toLowerCase().includes(q) || (t.league_name && t.league_name.toLowerCase().includes(q))
      ).slice(0, 5)
    : [];

  const filteredNews = q
    ? news.filter(
        (n) =>
          n.title.toLowerCase().includes(q) ||
          (n.summary && n.summary.toLowerCase().includes(q)) ||
          n.tags?.some((tag) => tag.toLowerCase().includes(q))
      ).slice(0, 5)
    : [];

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center space-x-2 bg-white/5 border border-white/10 hover:bg-white/10 text-slate-300 px-3.5 py-1.5 rounded-full text-xs transition-all cursor-pointer"
        title="Tezkor qidiruv (Ctrl + K)"
      >
        <Search className="w-3.5 h-3.5 text-emerald-400" />
        <span className="hidden sm:inline font-semibold">Qidirish...</span>
        <kbd className="hidden md:inline-block bg-white/10 px-1.5 py-0.5 rounded text-[10px] text-slate-400 font-mono">
          Ctrl K
        </kbd>
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 px-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="relative w-full max-w-2xl bg-[#0a1120] border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
            {/* Input Header */}
            <div className="flex items-center px-4 py-3 border-b border-white/10 bg-slate-900/50">
              <Search className="w-5 h-5 text-emerald-400 mr-3" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Jamoa, o'yin yoki yangilik nomini yozing..."
                className="w-full bg-transparent text-slate-100 placeholder-slate-500 text-sm focus:outline-none"
                autoFocus
              />
              {query && (
                <button onClick={() => setQuery("")} className="mr-2 text-slate-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-xs bg-white/10 hover:bg-white/20 text-slate-300 px-2 py-1 rounded"
              >
                ESC
              </button>
            </div>

            {/* Results body */}
            <div className="p-4 overflow-y-auto space-y-6 flex-1 text-xs">
              {loading && (
                <div className="text-center py-8 text-slate-400 animate-pulse">
                  Ma'lumotlar yuklanmoqda...
                </div>
              )}

              {!loading && !query && (
                <div className="text-center py-8 text-slate-500 space-y-2">
                  <Search className="w-8 h-8 mx-auto text-slate-600" />
                  <p>Qidiruv uchun kalit so'z yozing (masalan: Paxtakor, Real Madrid, Superliga)</p>
                </div>
              )}

              {!loading && query && (
                <>
                  {filteredMatches.length === 0 &&
                    filteredTeams.length === 0 &&
                    filteredNews.length === 0 && (
                      <div className="text-center py-8 text-slate-500">
                        "{query}" bo'yicha hech narsa topilmadi 📭
                      </div>
                    )}

                  {/* Matches */}
                  {filteredMatches.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center text-slate-400 font-bold uppercase tracking-wider text-[11px]">
                        <Trophy className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
                        <span>O'yinlar ({filteredMatches.length})</span>
                      </div>
                      <div className="space-y-1">
                        {filteredMatches.map((m) => (
                          <Link
                            key={m.id}
                            href={`/matches/${m.id}`}
                            onClick={() => setIsOpen(false)}
                            className="flex items-center justify-between p-2.5 rounded-xl bg-white/5 hover:bg-emerald-500/10 hover:border-emerald-500/30 border border-transparent transition-all"
                          >
                            <span className="font-semibold text-slate-200">
                              {m.home_team_name} vs {m.away_team_name}
                            </span>
                            <span className="text-[10px] text-slate-400 bg-white/5 px-2 py-0.5 rounded">
                              {m.league_name}
                            </span>
                          </Link>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Teams */}
                  {filteredTeams.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center text-slate-400 font-bold uppercase tracking-wider text-[11px]">
                        <Shield className="w-3.5 h-3.5 mr-1.5 text-cyan-400" />
                        <span>Jamoalar ({filteredTeams.length})</span>
                      </div>
                      <div className="space-y-1">
                        {filteredTeams.map((t) => (
                          <Link
                            key={t.slug}
                            href={`/teams/${t.slug}`}
                            onClick={() => setIsOpen(false)}
                            className="flex items-center justify-between p-2.5 rounded-xl bg-white/5 hover:bg-cyan-500/10 hover:border-cyan-500/30 border border-transparent transition-all"
                          >
                            <span className="font-semibold text-slate-200">{t.name}</span>
                            <span className="text-[10px] text-slate-400">{t.league_name}</span>
                          </Link>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* News */}
                  {filteredNews.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center text-slate-400 font-bold uppercase tracking-wider text-[11px]">
                        <Newspaper className="w-3.5 h-3.5 mr-1.5 text-amber-400" />
                        <span>Yangiliklar ({filteredNews.length})</span>
                      </div>
                      <div className="space-y-1">
                        {filteredNews.map((n) => (
                          <Link
                            key={n.id}
                            href={`/news/${n.slug}`}
                            onClick={() => setIsOpen(false)}
                            className="flex flex-col p-2.5 rounded-xl bg-white/5 hover:bg-amber-500/10 hover:border-amber-500/30 border border-transparent transition-all space-y-1"
                          >
                            <span className="font-semibold text-slate-200 line-clamp-1">
                              {n.title}
                            </span>
                            <span className="text-[10px] text-slate-400 line-clamp-1">
                              {n.summary}
                            </span>
                          </Link>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
