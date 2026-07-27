"use client";

import { useEffect, useState } from "react";
import { 
  Database, 
  Play, 
  Sparkles, 
  PlusCircle, 
  Edit3 
} from "lucide-react";
import { 
  getLocalMatches, 
  getLocalNews, 
  saveLocalMatches, 
  saveLocalNews, 
  simulateLocalTick, 
  Match,
  NewsItem
} from "../../lib/mockStore";
import { apiUrl } from "../../lib/api";

export default function AdminDashboard() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [seedStatus, setSeedStatus] = useState<string>("");
  const [simStatus, setSimStatus] = useState<string>("");
  const [newsTopic, setNewsTopic] = useState<string>("");
  const [newsStatus, setNewsStatus] = useState<string>("");
  const [editingMatch, setEditingMatch] = useState<Match | null>(null);
  const [isOffline, setIsOffline] = useState(false);
  
  // Authorization states
  const [enteredPasskey, setEnteredPasskey] = useState("");
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [authError, setAuthError] = useState("");
  
  // Custom manual override state
  const [overrideHomeScore, setOverrideHomeScore] = useState<number>(0);
  const [overrideAwayScore, setOverrideAwayScore] = useState<number>(0);
  const [overrideStatus, setOverrideStatus] = useState<string>("LIVE");
  const [overrideMinute, setOverrideMinute] = useState<number>(0);

  const handleAuthSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Simple secure check for demo purposes, can check settings.SECRET_KEY or hardcoded 'admin123'
    if (enteredPasskey === "admin123") {
      setIsAuthorized(true);
      setAuthError("");
    } else {
      setAuthError("Noto'g'ri maxfiy kalit! ❌");
    }
  };

  const fetchMatches = async () => {
    try {
      const res = await fetch(apiUrl("/matches/"));
      if (res.ok) {
        setMatches(await res.json());
        setIsOffline(false);
      } else {
         throw new Error();
      }
    } catch (err) {
      console.warn("Backend offline, using local admin mode.");
      setIsOffline(true);
      setMatches(getLocalMatches());
    }
  };

  useEffect(() => {
    fetchMatches();
  }, []);

  const triggerSeed = async () => {
    setSeedStatus("Seeding...");
    if (isOffline) {
      // Seed locally by resetting localStorage matches to default
      localStorage.removeItem("local_matches");
      localStorage.removeItem("local_news");
      setMatches(getLocalMatches());
      setSeedStatus("Demo ma'lumotlar tiklandi! ✅");
      return;
    }

    try {
      const res = await fetch(apiUrl("/admin/seed"), {
        method: "POST",
        headers: { "X-Admin-Token": enteredPasskey },
      });
      if (res.ok) {
        setSeedStatus("Baza muvaffaqiyatli to'ldirildi! ✅");
        fetchMatches();
      } else {
        setSeedStatus("Xatolik yuz berdi ❌");
      }
    } catch (err) {
      setSeedStatus("Server ulanish xatosi ❌");
    }
  };

  const triggerSimulationStep = async () => {
    setSimStatus("Simulating...");
    if (isOffline) {
      const updated = simulateLocalTick();
      setMatches(updated);
      setSimStatus("Demo o'yinlar yangilandi! ⚽");
      return;
    }

    try {
      const res = await fetch(apiUrl("/admin/simulate"), {
        method: "POST",
        headers: { "X-Admin-Token": enteredPasskey },
      });
      if (res.ok) {
        setSimStatus("O'yin daqiqalari yangilandi! ⚽");
        fetchMatches();
      } else {
        setSimStatus("Simulyatsiya xatosi ❌");
      }
    } catch (err) {
      setSimStatus("Server ulanish xatosi ❌");
    }
  };

  const generateAINews = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newsTopic) return;
    setNewsStatus("AI yangilik generatsiya qilmoqda...");

    if (isOffline) {
      const newsList = getLocalNews();
      const slug = newsTopic.toLowerCase().replace(/[^a-z0-9]+/g, "-");
      const newArticle: NewsItem = {
        id: Date.now(),
        title: `AI Tahlil: ${newsTopic}`,
        slug,
        summary: `Sun'iy intellekt tomonidan ${newsTopic} haqida tayyorlangan ekspert xulosasi.`,
        content: `Ushbu maqolada biz ${newsTopic} mavzusini tahlil qilamiz.\n\nEkspertlarimiz fikriga ko'ra, yaqin kunlarda sport olamida katta o'zgarishlar kutilmoqda. Batafsil ma'lumotlar tez kunda e'lon qilinadi.`,
        created_at: new Date().toISOString(),
        tags: ["ai-tahlil", "futbol-news"]
      };
      saveLocalNews([newArticle, ...newsList]);
      setNewsStatus("Demo AI yangilik yaratildi! 📰✨");
      setNewsTopic("");
      return;
    }

    try {
      const res = await fetch(apiUrl("/admin/generate-news"), {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Admin-Token": enteredPasskey },
        body: JSON.stringify({ topic: newsTopic })
      });
      if (res.ok) {
        setNewsStatus("AI yangilik maqolasi yaratildi va chop etildi! 📰✨");
        setNewsTopic("");
      } else {
        setNewsStatus("Generatsiyada xatolik yuz berdi ❌");
      }
    } catch (err) {
      setNewsStatus("Server ulanish xatosi ❌");
    }
  };

  const startEditMatch = (m: Match) => {
    setEditingMatch(m);
    setOverrideHomeScore(m.score_home);
    setOverrideAwayScore(m.score_away);
    setOverrideStatus(m.status);
    setOverrideMinute(m.minute);
  };

  const saveMatchOverride = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingMatch) return;

    if (isOffline) {
      const list = getLocalMatches();
      const updated = list.map(m => {
        if (m.id === editingMatch.id) {
          return {
            ...m,
            score_home: overrideHomeScore,
            score_away: overrideAwayScore,
            status: overrideStatus,
            minute: overrideMinute
          };
        }
        return m;
      });
      saveLocalMatches(updated);
      setMatches(updated);
      setEditingMatch(null);
      return;
    }

    try {
      const res = await fetch(apiUrl(`/admin/matches/${editingMatch.id}`), {
        method: "PUT",
        headers: { "Content-Type": "application/json", "X-Admin-Token": enteredPasskey },
        body: JSON.stringify({
          score_home: overrideHomeScore,
          score_away: overrideAwayScore,
          status: overrideStatus,
          minute: overrideMinute
        })
      });
      if (res.ok) {
        setEditingMatch(null);
        fetchMatches();
      } else {
        alert("Saqlashda xatolik yuz berdi.");
      }
    } catch (err) {
      alert("Server ulanish xatosi.");
    }
  };
  if (!isAuthorized) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] max-w-md mx-auto space-y-6">
        <div className="glass-panel p-8 rounded-3xl w-full border border-white/10 space-y-6 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/10 rounded-full blur-2xl" />
          <div className="text-center space-y-2 relative z-10">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-cyan-500/10 text-cyan-400 mb-2 border border-cyan-500/25 text-lg">
              🔒
            </div>
            <h2 className="text-xl font-bold tracking-tight">Admin Autentifikatsiyasi</h2>
            <p className="text-xs text-slate-450 leading-relaxed">Simulyator va kontentni boshqarish uchun maxfiy kalitni kiriting.</p>
            <p className="text-[10px] text-slate-600">Demo kalit: <code className="bg-white/5 px-1 py-0.5 rounded text-cyan-400 font-mono">admin123</code></p>
          </div>

          <form onSubmit={handleAuthSubmit} className="space-y-4 relative z-10">
            <div className="space-y-2">
              <label className="text-xs text-slate-400 font-semibold">Maxfiy Kalit (Passkey):</label>
              <input 
                type="password" 
                placeholder="Parolni yozing..."
                value={enteredPasskey}
                onChange={(e) => setEnteredPasskey(e.target.value)}
                className="w-full bg-slate-950 border border-white/10 rounded-xl px-3 py-2.5 text-xs text-slate-100 placeholder:text-slate-700 focus:outline-none focus:border-cyan-500"
              />
            </div>
            {authError && <p className="text-xs text-rose-400 font-medium">{authError}</p>}
            <button 
              type="submit"
              className="w-full bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-bold py-2.5 px-4 rounded-xl transition-all text-xs cursor-pointer shadow-lg shadow-cyan-500/10"
            >
              Tasdiqlash 🔑
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Admin & Simulyator Boshqaruvi</h1>
          <p className="text-slate-400 text-sm mt-1">Loyiha ishlashini tekshirish uchun o'yinlarni boshqaring, AI yangiliklar va tahlillar yarating.</p>
        </div>
        {isOffline && (
           <span className="bg-cyan-500/10 text-cyan-400 border border-cyan-500/25 px-4 py-1.5 rounded-full text-xs font-bold shadow-sm">
             Lokal Demo Rejimi Faol 🟢
           </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="glass-panel p-6 rounded-2xl space-y-6">
          <h2 className="text-lg font-bold flex items-center text-emerald-400">
             <Database className="w-5 h-5 mr-2" /> Baza & Simulyator
          </h2>
          
          <div className="space-y-4 text-sm">
            <div className="space-y-2">
              <button 
                onClick={triggerSeed}
                className="w-full bg-slate-800 hover:bg-slate-700 text-slate-100 font-bold py-2.5 px-4 rounded-xl transition-all text-xs flex items-center justify-center space-x-2 border border-white/5 cursor-pointer"
              >
                <PlusCircle className="w-4 h-4" />
                <span>{isOffline ? "Demo ma'lumotlarni tiklash" : "Baza ma'lumotlarini seed qilish"}</span>
              </button>
              {seedStatus && <p className="text-[11px] text-slate-400">{seedStatus}</p>}
            </div>

            <div className="space-y-2 pt-2 border-t border-white/5">
              <p className="text-xs text-slate-500">
                O'yin daqiqalarini oshirish, gollar va kartochkalar yaratish hamda live yangilanishlarni ko'rish uchun pastdagi tugmani bosing.
              </p>
              <button 
                onClick={triggerSimulationStep}
                className="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold py-2.5 px-4 rounded-xl transition-all text-xs flex items-center justify-center space-x-2 shadow-lg shadow-emerald-500/10 cursor-pointer"
              >
                <Play className="w-4 h-4" />
                <span>Simulyatsiyani 1-qadam oldinga surish</span>
              </button>
              {simStatus && <p className="text-[11px] text-emerald-400">{simStatus}</p>}
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl space-y-6">
          <h2 className="text-lg font-bold flex items-center text-cyan-400">
             <Sparkles className="w-5 h-5 mr-2" /> AI Yangilik Generatsiyasi
          </h2>

          <form onSubmit={generateAINews} className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs text-slate-400 font-medium">Yangilik mavzusi:</label>
              <input 
                type="text" 
                placeholder="Masalan: Mbappe Real Madriddagi debyuti haqida gapirdi"
                value={newsTopic}
                onChange={(e) => setNewsTopic(e.target.value)}
                className="w-full bg-slate-950/60 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500"
              />
            </div>
            
            <button 
              type="submit"
              className="w-full bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-bold py-2.5 px-4 rounded-xl transition-all text-xs flex items-center justify-center space-x-2 cursor-pointer"
            >
              <Sparkles className="w-4 h-4" />
              <span>AI Yangilik Yaratish</span>
            </button>
            {newsStatus && <p className="text-[11px] text-cyan-400">{newsStatus}</p>}
          </form>
        </div>

        <div className="glass-panel p-6 rounded-2xl space-y-6 md:col-span-3">
          <h2 className="text-lg font-bold">O'yinlarni qo'lda boshqarish (Manual Override)</h2>

          {editingMatch ? (
            <form onSubmit={saveMatchOverride} className="bg-slate-950/40 p-4 rounded-2xl border border-white/5 space-y-4 max-w-xl">
              <div className="flex items-center justify-between border-b border-white/5 pb-2">
                 <h3 className="font-bold text-xs">O'yinni tahrirlash: {editingMatch.home_team_name} vs {editingMatch.away_team_name}</h3>
                 <button 
                   type="button" 
                   onClick={() => setEditingMatch(null)}
                   className="text-xs text-slate-500 hover:text-slate-300"
                 >
                   Bekor qilish
                 </button>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 uppercase font-semibold">{editingMatch.home_team_name} (Gol):</label>
                  <input 
                    type="number" 
                    value={overrideHomeScore}
                    onChange={(e) => setOverrideHomeScore(parseInt(e.target.value))}
                    className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs focus:outline-none"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 uppercase font-semibold">{editingMatch.away_team_name} (Gol):</label>
                  <input 
                    type="number" 
                    value={overrideAwayScore}
                    onChange={(e) => setOverrideAwayScore(parseInt(e.target.value))}
                    className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs focus:outline-none"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 uppercase font-semibold">Status:</label>
                  <select 
                    value={overrideStatus}
                    onChange={(e) => setOverrideStatus(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs focus:outline-none"
                  >
                    <option value="NS">NS (Boshlanmagan)</option>
                    <option value="LIVE">LIVE (Jonli)</option>
                    <option value="FT">FT (Tugagan)</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 uppercase font-semibold">Daqiqa:</label>
                  <input 
                    type="number" 
                    value={overrideMinute}
                    onChange={(e) => setOverrideMinute(parseInt(e.target.value))}
                    className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs focus:outline-none"
                  />
                </div>
              </div>

              <button 
                type="submit" 
                className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs cursor-pointer"
              >
                O'zgarishlarni saqlash
              </button>
            </form>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead>
                  <tr className="border-b border-white/5 text-slate-500 uppercase tracking-wider">
                    <th className="py-3 px-4 font-semibold">Liga</th>
                    <th className="py-3 px-4 font-semibold">Bahs</th>
                    <th className="py-3 px-4 font-semibold text-center">Hisob</th>
                    <th className="py-3 px-4 font-semibold">Status</th>
                    <th className="py-3 px-4 font-semibold">Daqiqa</th>
                    <th className="py-3 px-4 font-semibold text-right">Amallar</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {matches.map((m) => (
                    <tr key={m.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="py-3.5 px-4 font-medium text-slate-400">{m.league_name}</td>
                      <td className="py-3.5 px-4 font-semibold text-slate-200">{m.home_team_name} - {m.away_team_name}</td>
                      <td className="py-3.5 px-4 text-center font-extrabold">{m.score_home} - {m.score_away}</td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                           m.status === "LIVE" ? "bg-rose-500/10 text-rose-400" : m.status === "FT" ? "bg-slate-500/10 text-slate-400" : "bg-cyan-500/10 text-cyan-400"
                        }`}>
                          {m.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-400">{m.minute}'</td>
                      <td className="py-3.5 px-4 text-right">
                        <button 
                          onClick={() => startEditMatch(m)}
                          className="text-cyan-400 hover:text-cyan-300 font-semibold inline-flex items-center cursor-pointer"
                        >
                          <Edit3 className="w-3.5 h-3.5 mr-1" /> Tahrirlash
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
