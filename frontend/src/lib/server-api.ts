import { unstable_rethrow } from "next/navigation";

import type { Match, NewsItem } from "./types";

/**
 * Server komponentlar uchun ma'lumot olish.
 *
 * Nima uchun alohida: brauzer backendga tashqi manzil orqali murojaat qiladi
 * (NEXT_PUBLIC_API_URL), server esa ichki tarmoq orqali tezroq va xavfsizroq
 * bora oladi (API_INTERNAL_URL). Deploy'da ikkalasi turlicha bo'lishi mumkin.
 *
 * Next.js 16 da `fetch` standart holatda keshlanmaydi — jonli hisoblar uchun
 * aynan shu kerak, har bir so'rovda yangi ma'lumot olinadi.
 */

const BASE_URL =
  process.env.API_INTERNAL_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

/** Backend ishlamasa sayt ishdan chiqmasligi kerak — null/bo'sh ro'yxat qaytaramiz. */
async function getJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${BASE_URL}/api/v1${path}`, {
      // Jonli ma'lumot: keshlanmaydi
      cache: "no-store",
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) return fallback;
    return (await res.json()) as T;
  } catch (error) {
    // Next.js ba'zi ichki signallarni xato ko'rinishida tashlaydi
    // (`no-store` fetch sahifani dinamik deb belgilash uchun, notFound() va h.k.).
    // Ularni ushlab qolsak framework noto'g'ri ishlaydi — qaytarib tashlaymiz.
    unstable_rethrow(error);
    console.error(`Backenddan ma'lumot olinmadi (${path}):`, error);
    return fallback;
  }
}

export async function getMatches(): Promise<Match[]> {
  return getJson<Match[]>("/matches/?limit=100", []);
}

export async function getMatch(id: string): Promise<Match | null> {
  return getJson<Match | null>(`/matches/${encodeURIComponent(id)}`, null);
}

export async function getNews(): Promise<NewsItem[]> {
  return getJson<NewsItem[]>("/news/?limit=50", []);
}

export async function getNewsArticle(slug: string): Promise<NewsItem | null> {
  return getJson<NewsItem | null>(`/news/${encodeURIComponent(slug)}`, null);
}
