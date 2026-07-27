/**
 * Vaqtni formatlash uchun yagona joy.
 *
 * Nima uchun timeZone qattiq belgilangan:
 *  1. Sayt O'zbekiston auditoriyasi uchun — o'yin vaqtlari Toshkent vaqtida
 *     ko'rsatilishi kerak, tashrif buyuruvchi qayerda bo'lishidan qat'i nazar.
 *  2. Server komponentlarida `new Date(...).toLocaleString()` serverning
 *     timezone'ini oladi, brauzerda esa foydalanuvchinikini — natijada
 *     Next.js gidratatsiya xatosi (hydration mismatch) chiqadi. Ikkala
 *     tomonda bir xil zona ishlatilsa, bunday muammo bo'lmaydi.
 *
 * Backend vaqtni `2026-07-05T04:14:37Z` ko'rinishida, ya'ni timezone belgisi
 * bilan qaytaradi (backend/app/core/clock.py ga qarang).
 */

export const MATCH_TIME_ZONE = "Asia/Tashkent";
const LOCALE = "uz-UZ";

/** "18:30" */
export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString(LOCALE, {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: MATCH_TIME_ZONE,
  });
}

/** "05.07.2026" */
export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(LOCALE, {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    timeZone: MATCH_TIME_ZONE,
  });
}

/** "5-iyul, 2026, 09:14" */
export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleDateString(LOCALE, {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: MATCH_TIME_ZONE,
  });
}
