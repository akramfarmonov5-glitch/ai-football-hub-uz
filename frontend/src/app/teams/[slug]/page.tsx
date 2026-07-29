import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { notFound } from "next/navigation";
import { cache } from "react";
import {
  ArrowLeft,
  MapPin,
  Users,
  Calendar,
  Globe,
  Trophy,
  Sparkles,
} from "lucide-react";

import { getTeam } from "../../../lib/server-api";
import { formatDate, formatTime } from "../../../lib/time";
import type { Match, TeamDetail } from "../../../lib/types";

type Props = { params: Promise<{ slug: string }> };

const loadTeam = cache(getTeam);

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const team = await loadTeam(slug);

  if (!team) return { title: "Jamoa topilmadi" };

  const qismlar = [team.league_name, team.stadium && `stadion: ${team.stadium}`]
    .filter(Boolean)
    .join(" · ");
  const description =
    team.description?.slice(0, 160) ||
    `${team.name} — o'yinlar jadvali, so'nggi natijalar va turnir jadvalidagi o'rni. ${qismlar}`;

  return {
    title: team.name,
    description,
    openGraph: {
      title: team.name,
      description,
      type: "profile",
      url: `/teams/${team.slug}`,
      images: team.badge ? [{ url: team.badge }] : undefined,
    },
    alternates: { canonical: `/teams/${team.slug}` },
  };
}

export default async function TeamPage({ params }: Props) {
  const { slug } = await params;
  const team = await loadTeam(slug);

  if (!team) notFound();

  return (
    <div className="space-y-8">
      <Link
        href="/"
        className="inline-flex items-center text-slate-400 hover:text-emerald-400 text-sm transition-colors"
      >
        <ArrowLeft className="w-4 h-4 mr-2" /> Bosh sahifaga qaytish
      </Link>

      <TeamHeader team={team} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {team.upcoming_matches.length > 0 && (
            <MatchSection
              title="Keyingi o'yinlar"
              matches={team.upcoming_matches}
              teamName={team.name}
            />
          )}
          {team.recent_matches.length > 0 && (
            <MatchSection
              title="So'nggi natijalar"
              matches={team.recent_matches}
              teamName={team.name}
              finished
            />
          )}
          {team.upcoming_matches.length === 0 && team.recent_matches.length === 0 && (
            <p className="text-sm text-slate-500 text-center py-12 glass-panel rounded-2xl">
              Bu jamoa uchun o'yinlar hozircha yo'q.
            </p>
          )}

          {team.description && (
            <section className="glass-panel p-6 rounded-2xl space-y-3">
              <h2 className="text-base font-bold">Jamoa haqida</h2>
              <p className="text-sm text-slate-400 leading-relaxed whitespace-pre-line">
                {team.description}
              </p>
              {team.description_translated && (
                <p className="text-[11px] text-slate-600 flex items-center gap-1.5 pt-1">
                  <Sparkles className="w-3 h-3" />
                  Matn sun'iy intellekt tomonidan o'zbek tiliga o'girilgan
                </p>
              )}
            </section>
          )}
        </div>

        <div className="space-y-6">
          {team.standing && <StandingCard team={team} />}
          <InfoCard team={team} />
        </div>
      </div>
    </div>
  );
}

function TeamHeader({ team }: { team: TeamDetail }) {
  return (
    <div className="glass-panel rounded-3xl p-6 md:p-8 flex flex-col sm:flex-row items-center gap-6">
      <div className="w-20 h-20 md:w-24 md:h-24 shrink-0 bg-white/5 border border-white/5 rounded-2xl flex items-center justify-center p-3">
        {team.badge ? (
          <Image
            src={team.badge}
            alt={team.name}
            width={72}
            height={72}
            className="w-full h-full object-contain"
            unoptimized
          />
        ) : (
          <span className="text-3xl font-black text-emerald-400">
            {team.name.substring(0, 2).toUpperCase()}
          </span>
        )}
      </div>

      <div className="text-center sm:text-left space-y-2">
        <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">{team.name}</h1>
        <div className="flex flex-wrap justify-center sm:justify-start gap-2 text-xs">
          {team.league_name && (
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/5 text-slate-300">
              {team.league_name}
            </span>
          )}
          {team.country && (
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/5 text-slate-400">
              {team.country}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

function StandingCard({ team }: { team: TeamDetail }) {
  const s = team.standing!;
  return (
    <div className="glass-panel p-5 rounded-2xl space-y-4">
      <h2 className="font-bold text-sm flex items-center gap-2">
        <Trophy className="w-4 h-4 text-emerald-400" />
        Yetakchi beshlikda
      </h2>

      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-black text-emerald-400">{s.position}</span>
        <span className="text-xs text-slate-500">-o'rin</span>
      </div>

      <dl className="grid grid-cols-2 gap-y-2 text-xs">
        <Stat label="O'yin" value={s.played} />
        <Stat label="Ochko" value={s.points} strong />
        <Stat label="G'alaba" value={s.won} />
        <Stat label="Durang" value={s.drawn} />
        <Stat label="Mag'lubiyat" value={s.lost} />
        <Stat
          label="Gollar farqi"
          value={s.goal_difference > 0 ? `+${s.goal_difference}` : s.goal_difference}
        />
      </dl>

      <Link
        href="/standings"
        className="block text-center text-xs text-cyan-400 hover:underline pt-1"
      >
        Barcha ligalar bo'yicha ko'rish
      </Link>
    </div>
  );
}

function Stat({
  label,
  value,
  strong = false,
}: {
  label: string;
  value: string | number;
  strong?: boolean;
}) {
  return (
    <div>
      <dt className="text-slate-500">{label}</dt>
      <dd className={strong ? "font-black text-slate-100" : "font-semibold text-slate-300"}>
        {value}
      </dd>
    </div>
  );
}

function InfoCard({ team }: { team: TeamDetail }) {
  const qatorlar = [
    team.stadium && { icon: MapPin, label: "Stadion", value: team.stadium },
    team.stadium_capacity && {
      icon: Users,
      label: "Sig'imi",
      value: `${team.stadium_capacity.toLocaleString("uz-UZ")} o'rin`,
    },
    team.location && { icon: MapPin, label: "Joylashuvi", value: team.location },
    team.founded && { icon: Calendar, label: "Tashkil topgan", value: String(team.founded) },
  ].filter(Boolean) as { icon: typeof MapPin; label: string; value: string }[];

  if (qatorlar.length === 0 && !team.website) return null;

  return (
    <div className="glass-panel p-5 rounded-2xl space-y-4">
      <h2 className="font-bold text-sm">Ma'lumot</h2>
      <dl className="space-y-3 text-xs">
        {qatorlar.map(({ icon: Icon, label, value }) => (
          <div key={label} className="flex items-start gap-2">
            <Icon className="w-3.5 h-3.5 text-slate-500 mt-0.5 shrink-0" />
            <div>
              <dt className="text-slate-500">{label}</dt>
              <dd className="font-semibold text-slate-300">{value}</dd>
            </div>
          </div>
        ))}
        {team.website && (
          <div className="flex items-start gap-2">
            <Globe className="w-3.5 h-3.5 text-slate-500 mt-0.5 shrink-0" />
            <div>
              <dt className="text-slate-500">Sayt</dt>
              <dd>
                <a
                  href={`https://${team.website.replace(/^https?:\/\//, "")}`}
                  target="_blank"
                  rel="noreferrer"
                  className="font-semibold text-cyan-400 hover:underline break-all"
                >
                  {team.website}
                </a>
              </dd>
            </div>
          </div>
        )}
      </dl>
    </div>
  );
}

function MatchSection({
  title,
  matches,
  teamName,
  finished = false,
}: {
  title: string;
  matches: Match[];
  teamName: string;
  finished?: boolean;
}) {
  return (
    <section className="space-y-3">
      <h2 className="text-base font-bold">{title}</h2>
      <div className="glass-panel rounded-2xl divide-y divide-white/5">
        {matches.map((m) => (
          <TeamMatchRow key={m.id} match={m} teamName={teamName} finished={finished} />
        ))}
      </div>
    </section>
  );
}

function TeamMatchRow({
  match,
  teamName,
  finished,
}: {
  match: Match;
  teamName: string;
  finished: boolean;
}) {
  const uyda = match.home_team_name === teamName;
  const raqib = uyda ? match.away_team_name : match.home_team_name;
  const oz = uyda ? match.score_home : match.score_away;
  const raqibHisob = uyda ? match.score_away : match.score_home;

  // Natija belgisi faqat tugagan o'yinlarda ma'noga ega
  const natija = !finished ? null : oz > raqibHisob ? "W" : oz < raqibHisob ? "L" : "D";
  const natijaStyle =
    natija === "W"
      ? "bg-emerald-500/20 text-emerald-400"
      : natija === "L"
        ? "bg-rose-500/20 text-rose-400"
        : "bg-slate-500/20 text-slate-400";

  return (
    <Link
      href={`/matches/${match.id}`}
      className="flex items-center gap-3 p-4 hover:bg-white/[0.02] transition-colors"
    >
      <span className="text-[10px] text-slate-500 w-20 shrink-0">
        {formatDate(match.match_time)}
      </span>

      <span className="text-[9px] font-bold text-slate-500 uppercase w-8 shrink-0">
        {uyda ? "uyda" : "mehm."}
      </span>

      <span className="flex-1 text-sm font-semibold text-slate-200 truncate">{raqib}</span>

      {finished ? (
        <>
          <span className="text-sm font-black text-slate-100 tabular-nums">
            {oz}:{raqibHisob}
          </span>
          {natija && (
            <span
              className={`w-5 h-5 rounded flex items-center justify-center text-[9px] font-black ${natijaStyle}`}
            >
              {natija}
            </span>
          )}
        </>
      ) : (
        <span className="text-xs font-bold text-cyan-400">
          {match.status === "LIVE" ? "JONLI" : formatTime(match.match_time)}
        </span>
      )}
    </Link>
  );
}
