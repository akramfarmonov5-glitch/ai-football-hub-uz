import type { Metadata } from "next";
import Link from "next/link";
import { Trophy } from "lucide-react";

import { getMeta, getStandings } from "../../lib/server-api";
import { StandingsTable } from "../../components/StandingsTable";

// Manba (TheSportsDB bepul tarifi) jadvalning faqat birinchi 5 qatorini
// beradi. Shuning uchun sahifa "to'liq turnir jadvali" deb atalmaydi —
// aks holda tashrif buyuruvchi ligada 5 ta jamoa bor deb o'ylardi.
export const metadata: Metadata = {
  title: "Yetakchi beshlik",
  description:
    "O'zbekiston Superligasi va Yevropa ligalarida yetakchi beshlik: ochkolar, gollar farqi va jamoalar formasi.",
  openGraph: {
    title: "Yetakchi beshlik",
    description:
      "Ligalar bo'yicha yetakchi beshlik: ochkolar, gollar farqi va oxirgi 5 o'yin formasi.",
    url: "/standings",
  },
  alternates: { canonical: "/standings" },
};

export default async function StandingsPage() {
  const [leagues, meta] = await Promise.all([getStandings(), getMeta()]);

  if (leagues.length === 0) {
    return (
      <div className="space-y-6">
        <PageHeader />
        <p className="text-sm text-slate-500 text-center py-16 glass-panel rounded-2xl">
          Jadval hali bo'sh — u tugagan o'yinlar asosida hisoblanadi.
          <br />
          Birinchi o'yin yakunlangach shu yerda paydo bo'ladi.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader />

      {/* Ligalar orasida tez o'tish */}
      {leagues.length > 1 && (
        <nav className="flex flex-wrap gap-2" aria-label="Ligalar">
          {leagues.map((league) => (
            <a
              key={league.league_id}
              href={`#liga-${league.league_id}`}
              className="px-4 py-1.5 rounded-full text-xs font-bold bg-white/5 border border-white/5 text-slate-400 hover:bg-white/10 hover:text-slate-200 transition-colors"
            >
              {league.league_name}
            </a>
          ))}
        </nav>
      )}

      <div className="space-y-10">
        {leagues.map((league) => (
          <StandingsTable key={league.league_id} league={league} />
        ))}
      </div>

      <p className="text-[11px] text-slate-600 leading-relaxed border-t border-white/5 pt-4">
        {meta.is_simulated ? (
          <>
            Jadval tugagan o'yinlar asosida avtomatik hisoblanadi: g'alaba — 3
            ochko, durang — 1 ochko. Ochkolar teng bo'lganda gollar farqi, keyin
            urilgan gollar soni hisobga olinadi.
          </>
        ) : (
          <>
            Ma'lumot rasmiy manbadan olinadi va muntazam yangilanib turadi.
            Manba tarifi jadvalning faqat <strong>birinchi 5 o'rnini</strong>{" "}
            beradi, shuning uchun to'liq turnir jadvali emas, yetakchi beshlik
            ko'rsatiladi. Mavsumi hali boshlanmagan ligalar chiqarilmaydi.
          </>
        )}{" "}
        <Link href="/" className="text-cyan-400 hover:underline">
          O'yin markaziga qaytish
        </Link>
      </p>
    </div>
  );
}

function PageHeader() {
  return (
    <div className="space-y-1">
      <h1 className="text-2xl font-extrabold tracking-tight flex items-center gap-2">
        <Trophy className="w-6 h-6 text-emerald-400" />
        Yetakchi beshlik
      </h1>
      <p className="text-sm text-slate-400">
        Ligalar bo'yicha eng yuqori 5 o'rin: ochkolar, gollar farqi va forma.
      </p>
    </div>
  );
}
