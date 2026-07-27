/**
 * Vaqtni formatlash uchun yagona joy.
 *
 * Ikkita muammoni birdan hal qiladi:
 *
 * 1. **Vaqt zonasi.** Sayt O'zbekiston auditoriyasi uchun — o'yin vaqtlari
 *    Toshkent vaqtida ko'rsatiladi, tashrif buyuruvchi qayerda bo'lishidan
 *    qat'i nazar.
 *
 * 2. **Server va brauzer bir xil natija berishi.** `toLocaleDateString("uz-UZ")`
 *    ni ishlatib bo'lmaydi: Node'ning ICU ma'lumotlari brauzernikidan farq
 *    qiladi va bitta sana ikki xil chiqadi (server `2026-07-05`, brauzer
 *    `05/07/2026`) — natijada Next.js gidratatsiya xatosi beradi.
 *    Shuning uchun `formatToParts` orqali faqat raqamlar olinadi va satr
 *    qo'lda yig'iladi; oy nomlari ham shu yerda, lokalga bog'liq emas.
 *
 * Backend vaqtni `2026-07-05T04:14:37Z` ko'rinishida, ya'ni timezone belgisi
 * bilan qaytaradi (backend/app/core/clock.py ga qarang).
 */

export const MATCH_TIME_ZONE = "Asia/Tashkent";

const OY_NOMLARI = [
  "yanvar",
  "fevral",
  "mart",
  "aprel",
  "may",
  "iyun",
  "iyul",
  "avgust",
  "sentabr",
  "oktabr",
  "noyabr",
  "dekabr",
];

// `en-US` + raqamli parametrlar: raqamlar hamma muhitda bir xil chiqadi,
// ajratuvchilar va tartib esa bizga kerak emas — satrni o'zimiz yig'amiz.
const formatter = new Intl.DateTimeFormat("en-US", {
  timeZone: MATCH_TIME_ZONE,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hourCycle: "h23",
});

interface Qismlar {
  year: string;
  month: string;
  day: string;
  hour: string;
  minute: string;
}

function qismlar(iso: string): Qismlar | null {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return null;

  const result: Record<string, string> = {};
  for (const part of formatter.formatToParts(date)) {
    if (part.type !== "literal") result[part.type] = part.value;
  }
  return result as unknown as Qismlar;
}

/** "18:30" */
export function formatTime(iso: string): string {
  const q = qismlar(iso);
  return q ? `${q.hour}:${q.minute}` : "—";
}

/** "05.07.2026" */
export function formatDate(iso: string): string {
  const q = qismlar(iso);
  return q ? `${q.day}.${q.month}.${q.year}` : "—";
}

/** "5-iyul, 2026, 09:14" */
export function formatDateTime(iso: string): string {
  const q = qismlar(iso);
  if (!q) return "—";

  const kun = Number(q.day);
  const oy = OY_NOMLARI[Number(q.month) - 1] ?? q.month;
  return `${kun}-${oy}, ${q.year}, ${q.hour}:${q.minute}`;
}
