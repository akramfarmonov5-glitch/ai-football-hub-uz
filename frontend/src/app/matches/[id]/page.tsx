import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { cache } from "react";

import { getMatch } from "../../../lib/server-api";
import { formatDateTime } from "../../../lib/time";
import { liveLabel } from "../../../lib/matchStatus";
import { MatchDetailClient } from "../../../components/MatchDetailClient";

type Props = { params: Promise<{ id: string }> };

// generateMetadata va sahifaning o'zi bir xil ma'lumotni so'raydi —
// React cache ikkinchi so'rovni oldini oladi.
const loadMatch = cache(getMatch);

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const match = await loadMatch(id);

  if (!match) {
    return { title: "O'yin topilmadi" };
  }

  const teams = `${match.home_team_name} - ${match.away_team_name}`;
  const score =
    match.status === "NS" ? "" : ` ${match.score_home}:${match.score_away}`;
  const statusText =
    match.status === "LIVE"
      ? liveLabel(match)
      : match.status === "FT"
        ? "Yakunlandi"
        : formatDateTime(match.match_time);

  const title = `${teams}${score} — ${statusText}`;
  const description =
    match.ai_preview?.replace(/[*#]/g, "").slice(0, 160) ??
    `${match.league_name}: ${teams}. Jonli hisob, statistika va AI tahlili.`;

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      type: "article",
      url: `/matches/${match.id}`,
    },
    twitter: { card: "summary_large_image", title, description },
    alternates: { canonical: `/matches/${match.id}` },
  };
}

export default async function MatchDetailPage({ params }: Props) {
  const { id } = await params;
  const match = await loadMatch(id);

  if (!match) notFound();

  return <MatchDetailClient initialMatch={match} />;
}
