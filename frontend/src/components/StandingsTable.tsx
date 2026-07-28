import Image from "next/image";
import Link from "next/link";
import { teamSlug } from "../lib/teamSlug";
import type { FormResult, LeagueStandings } from "../lib/types";

/**
 * Bitta liganing turnir jadvali. Server komponent — interaktivlik kerak emas,
 * shuning uchun brauzerga hech qanday JavaScript yuborilmaydi.
 */
export function StandingsTable({ league }: { league: LeagueStandings }) {
  const total = league.table.length;

  return (
    <section id={`liga-${league.league_id}`} className="space-y-4 scroll-mt-20">
      <h2 className="text-lg font-black flex items-center gap-2">
        <span className="w-1.5 h-5 rounded-full bg-gradient-to-b from-emerald-400 to-cyan-400" />
        {league.league_name}
      </h2>

      {/* Keng jadval kichik ekranda sahifani emas, o'zini suradi */}
      <div className="glass-panel rounded-2xl overflow-x-auto">
        <table className="w-full text-xs min-w-[560px]">
          <caption className="sr-only">
            {league.league_name} turnir jadvali: o'rin, jamoa, o'yinlar, g'alaba,
            durang, mag'lubiyat, gollar va ochkolar
          </caption>
          <thead>
            <tr className="text-slate-500 uppercase tracking-wider border-b border-white/5">
              <th scope="col" className="py-3 pl-4 pr-2 text-left font-semibold w-8">#</th>
              <th scope="col" className="py-3 px-2 text-left font-semibold">Jamoa</th>
              <th scope="col" className="py-3 px-2 text-center font-semibold" title="O'yinlar">O</th>
              <th scope="col" className="py-3 px-2 text-center font-semibold hidden sm:table-cell" title="G'alaba">G</th>
              <th scope="col" className="py-3 px-2 text-center font-semibold hidden sm:table-cell" title="Durang">D</th>
              <th scope="col" className="py-3 px-2 text-center font-semibold hidden sm:table-cell" title="Mag'lubiyat">M</th>
              <th scope="col" className="py-3 px-2 text-center font-semibold hidden md:table-cell" title="Urilgan - o'tkazilgan gollar">Gollar</th>
              <th scope="col" className="py-3 px-2 text-center font-semibold" title="Gollar farqi">F</th>
              <th scope="col" className="py-3 px-2 text-center font-black text-slate-300" title="Ochko">O'</th>
              <th scope="col" className="py-3 pr-4 pl-2 text-right font-semibold hidden lg:table-cell">Forma</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {league.table.map((row) => (
              <tr key={row.team} className="hover:bg-white/[0.02] transition-colors">
                <td className="py-3 pl-4 pr-2">
                  <span
                    className={`inline-flex items-center justify-center w-5 h-5 rounded text-[10px] font-black ${positionStyle(
                      row.position,
                      total
                    )}`}
                  >
                    {row.position}
                  </span>
                </td>
                <td className="py-3 px-2">
                  <Link
                    href={`/teams/${teamSlug(row.team)}`}
                    className="flex items-center gap-2 group"
                  >
                    <span className="w-6 h-6 shrink-0 bg-white/5 border border-white/5 rounded flex items-center justify-center p-0.5">
                      {row.logo ? (
                        <Image
                          src={row.logo}
                          alt=""
                          width={20}
                          height={20}
                          className="w-full h-full object-contain"
                          unoptimized
                        />
                      ) : (
                        <span className="text-[9px] font-black text-slate-400">
                          {row.team.substring(0, 2).toUpperCase()}
                        </span>
                      )}
                    </span>
                    <span className="font-bold text-slate-200 whitespace-nowrap group-hover:text-emerald-400 transition-colors">
                      {row.team}
                    </span>
                  </Link>
                </td>
                <td className="py-3 px-2 text-center text-slate-400">{row.played}</td>
                <td className="py-3 px-2 text-center text-slate-400 hidden sm:table-cell">{row.won}</td>
                <td className="py-3 px-2 text-center text-slate-400 hidden sm:table-cell">{row.drawn}</td>
                <td className="py-3 px-2 text-center text-slate-400 hidden sm:table-cell">{row.lost}</td>
                <td className="py-3 px-2 text-center text-slate-400 hidden md:table-cell whitespace-nowrap">
                  {row.goals_for}:{row.goals_against}
                </td>
                <td
                  className={`py-3 px-2 text-center font-semibold ${
                    row.goal_difference > 0
                      ? "text-emerald-400"
                      : row.goal_difference < 0
                        ? "text-rose-400"
                        : "text-slate-400"
                  }`}
                >
                  {row.goal_difference > 0 ? `+${row.goal_difference}` : row.goal_difference}
                </td>
                <td className="py-3 px-2 text-center font-black text-slate-100">{row.points}</td>
                <td className="py-3 pr-4 pl-2 hidden lg:table-cell">
                  <div className="flex gap-1 justify-end">
                    {row.form.map((result, index) => (
                      <FormBadge key={index} result={result} />
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

/** Yuqori o'rinlar yashil, oxirgi o'rin qizil chiziq bilan ajratiladi. */
function positionStyle(position: number, total: number): string {
  if (position <= 2) return "bg-emerald-500/15 text-emerald-400";
  if (position === total && total > 3) return "bg-rose-500/15 text-rose-400";
  return "bg-white/5 text-slate-400";
}

const FORM_LABELS: Record<FormResult, string> = {
  W: "G'alaba",
  D: "Durang",
  L: "Mag'lubiyat",
};

function FormBadge({ result }: { result: FormResult }) {
  const style =
    result === "W"
      ? "bg-emerald-500/20 text-emerald-400"
      : result === "D"
        ? "bg-slate-500/20 text-slate-400"
        : "bg-rose-500/20 text-rose-400";

  return (
    <span
      title={FORM_LABELS[result]}
      className={`w-4 h-4 rounded-sm flex items-center justify-center text-[9px] font-black ${style}`}
    >
      {result}
    </span>
  );
}
