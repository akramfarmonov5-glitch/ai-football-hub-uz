import type { Match } from "./types";

/**
 * Jonli o'yin uchun ko'rsatiladigan yozuv.
 *
 * Manba (TheSportsDB bepul tarifi) o'tgan daqiqani bermaydi — `minute` doim 0
 * bo'lib keladi. Uni shundayligicha chiqarsak "JONLI 0'" degan **yolg'on**
 * ma'lumot chiqadi: o'yin allaqachon bir soatdan beri ketayotgan bo'lishi
 * mumkin. Daqiqa noma'lum bo'lsa uni umuman ko'rsatmaymiz.
 */
export function liveLabel(match: Pick<Match, "minute">, prefix = "JONLI"): string {
  const minute = match.minute ?? 0;
  return minute > 0 ? `${prefix} ${minute}'` : prefix;
}

/** Daqiqa ma'lum bo'lgandagina `48'` ko'rinishida, aks holda bo'sh satr. */
export function minuteLabel(match: Pick<Match, "minute">): string {
  const minute = match.minute ?? 0;
  return minute > 0 ? `${minute}'` : "";
}
