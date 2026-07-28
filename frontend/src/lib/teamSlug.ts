/**
 * Jamoa nomidan URL uchun slug.
 *
 * Backenddagi `app/services/teams.py:team_slug` bilan **aynan bir xil**
 * bo'lishi shart: havolalar shu yerda quriladi, sahifa esa backendda shu
 * slug bo'yicha topiladi. Biri o'zgarsa havolalar 404 beradi.
 *
 * Diakritik belgilar tashlab yuborilmaydi, balki lotin ekvivalentiga
 * o'giriladi: "Fenerbahçe" -> "fenerbahce", "Górnik" -> "gornik".
 */

// O'zbekcha apostroflar: "Mash'al" -> "mashal"
const APOSTROPHES = /['’‘`ʻʼ]/g;

// Unicode normalizatsiyasi ajratmaydigan harflar (alohida kod nuqtalari)
const SPECIAL: Record<string, string> = {
  ł: "l",
  ø: "o",
  đ: "d",
  ð: "d",
  þ: "th",
  ß: "ss",
  æ: "ae",
  œ: "oe",
};

export function teamSlug(name: string): string {
  let text = (name || "").toLowerCase().replace(APOSTROPHES, "");
  text = text.replace(/[łøđðþßæœ]/g, (ch) => SPECIAL[ch] ?? ch);

  // NFKD urg'uli harfni "harf + belgi" ga ajratadi, keyin belgilar olib
  // tashlanadi: ó -> o, ç -> c, é -> e
  text = text.normalize("NFKD").replace(/[̀-ͯ]/g, "");

  text = text
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/[\s-]+/g, "-")
    .replace(/^-+|-+$/g, "");

  return text.slice(0, 80).replace(/^-+|-+$/g, "") || "jamoa";
}
