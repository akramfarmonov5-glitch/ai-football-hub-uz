"use client";

import { useState, useEffect } from "react";
import { Star, Check, Sparkles } from "lucide-react";
import type { TeamSummary } from "../lib/types";

export function FavoriteTeamPicker() {
  const [favorite, setFavorite] = useState<string>("");
  const [isOpen, setIsOpen] = useState(false);
  const [teams, setTeams] = useState<TeamSummary[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem("favorite_team");
    if (saved) setFavorite(saved);

    const loadTeams = async () => {
      try {
        const api = process.env.NEXT_PUBLIC_API_URL || "https://futbol-backend-ewbc.onrender.com";
        const res = await fetch(`${api}/api/v1/teams/`);
        const data = await res.json();
        if (Array.isArray(data)) setTeams(data);
      } catch (err) {
        console.error("Jamoalarni yuklashda xato:", err);
      }
    };
    loadTeams();
  }, []);

  const selectTeam = (teamName: string) => {
    setFavorite(teamName);
    localStorage.setItem("favorite_team", teamName);
    setIsOpen(false);
    window.dispatchEvent(new Event("favorite_team_changed"));
  };

  const removeFavorite = () => {
    setFavorite("");
    localStorage.removeItem("favorite_team");
    setIsOpen(false);
    window.dispatchEvent(new Event("favorite_team_changed"));
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-bold transition-all border cursor-pointer ${
          favorite
            ? "bg-amber-500/10 text-amber-400 border-amber-500/30 hover:bg-amber-500/20"
            : "bg-white/5 border-white/10 text-slate-400 hover:bg-white/10 hover:text-slate-200"
        }`}
        title="Sevimli jamoangizni tanlang"
      >
        <Star className={`w-3.5 h-3.5 ${favorite ? "fill-amber-400 text-amber-400" : ""}`} />
        <span className="hidden lg:inline">{favorite || "Mening Jamoam"}</span>
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-md bg-[#0a1120] border border-white/10 rounded-2xl shadow-2xl overflow-hidden p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="text-base font-extrabold text-slate-100 flex items-center">
                <Sparkles className="w-4 h-4 mr-2 text-amber-400" />
                Sevimli Jamoangizni Tanlang
              </h3>
              <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-white text-xs">
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-400">
              Sevimli jamoangiz tanlansa, uning o'yinlari va tahlillari bosh sahifada oltin rangda ajratib ko'rsatiladi ⭐
            </p>

            <div className="max-h-64 overflow-y-auto space-y-1.5 pr-1 text-xs">
              {teams.length === 0 ? (
                <div className="text-center py-6 text-slate-500">Jamoalar yuklanmoqda...</div>
              ) : (
                teams.map((t) => (
                  <button
                    key={t.slug}
                    onClick={() => selectTeam(t.name)}
                    className={`w-full flex items-center justify-between p-2.5 rounded-xl border transition-all text-left cursor-pointer ${
                      favorite === t.name
                        ? "bg-amber-500/15 border-amber-500/40 text-amber-300 font-bold"
                        : "bg-white/5 border-white/5 text-slate-300 hover:bg-white/10"
                    }`}
                  >
                    <span>{t.name}</span>
                    {favorite === t.name && <Check className="w-4 h-4 text-amber-400" />}
                  </button>
                ))
              )}
            </div>

            {favorite && (
              <button
                onClick={removeFavorite}
                className="w-full py-2 text-center text-xs text-rose-400 hover:text-rose-300 underline"
              >
                Sevimli jamoani o'chirish
              </button>
            )}
          </div>
        </div>
      )}
    </>
  );
}
