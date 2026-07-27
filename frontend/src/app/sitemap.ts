import type { MetadataRoute } from "next";
import { getMatches, getNews } from "../lib/server-api";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

/** Qidiruv tizimlari uchun sayt xaritasi: /sitemap.xml */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [matches, news] = await Promise.all([getMatches(), getNews()]);

  return [
    {
      url: SITE_URL,
      lastModified: new Date(),
      changeFrequency: "hourly",
      priority: 1,
    },
    {
      url: `${SITE_URL}/standings`,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 0.9,
    },
    ...news.map((item) => ({
      url: `${SITE_URL}/news/${item.slug}`,
      lastModified: new Date(item.created_at),
      changeFrequency: "weekly" as const,
      priority: 0.8,
    })),
    ...matches.map((match) => ({
      url: `${SITE_URL}/matches/${match.id}`,
      lastModified: new Date(match.match_time),
      // Jonli o'yin tez-tez o'zgaradi, tugagani esa yo'q
      changeFrequency: match.status === "LIVE" ? ("hourly" as const) : ("weekly" as const),
      priority: match.status === "LIVE" ? 0.9 : 0.6,
    })),
  ];
}
