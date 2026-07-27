/**
 * G'alaba ehtimoli — backenddagi `app/services/probability.py` ning aynan
 * o'zi. Ilgari bu hisob bir necha joyda takrorlangan edi va katta hisob
 * farqida manfiy foiz chiqarardi (masalan 4:0 da `away = -20%`), natijada
 * progress-bar buzilardi.
 *
 * Kafolat: har bir qiymat musbat, yig'indisi aniq 100.
 */

export interface WinProbability {
  home: number;
  draw: number;
  away: number;
}

const BASE_HOME = 40;
const BASE_DRAW = 27;
const BASE_AWAY = 33;
const GOAL_WEIGHT = 16;
const MIN_PERCENT = 1;

export function estimateWinProbability(
  scoreHome: number,
  scoreAway: number,
  minute = 0,
  status = "LIVE"
): WinProbability {
  if (status === "FT") {
    if (scoreHome > scoreAway) return { home: 100, draw: 0, away: 0 };
    if (scoreHome < scoreAway) return { home: 0, draw: 0, away: 100 };
    return { home: 0, draw: 100, away: 0 };
  }

  const diff = scoreHome - scoreAway;
  const progress = Math.min(Math.max(minute, 0), 90) / 90;
  const weight = GOAL_WEIGHT * (0.6 + 0.8 * progress);

  const raw: WinProbability = {
    home: BASE_HOME + diff * weight,
    away: BASE_AWAY - diff * weight,
    draw: BASE_DRAW + (diff === 0 ? 12 * progress : -Math.abs(diff) * 4),
  };

  const clamped = {
    home: Math.max(MIN_PERCENT, raw.home),
    draw: Math.max(MIN_PERCENT, raw.draw),
    away: Math.max(MIN_PERCENT, raw.away),
  };

  const total = clamped.home + clamped.draw + clamped.away;
  const percents: WinProbability = {
    home: Math.round((clamped.home / total) * 100),
    draw: Math.round((clamped.draw / total) * 100),
    away: Math.round((clamped.away / total) * 100),
  };

  // Yaxlitlashdan keyingi 1% farqni eng katta ulushga qo'shamiz
  const drift = 100 - (percents.home + percents.draw + percents.away);
  if (drift !== 0) {
    const leader = (Object.keys(percents) as (keyof WinProbability)[]).reduce((a, b) =>
      percents[a] >= percents[b] ? a : b
    );
    percents[leader] += drift;
  }

  return percents;
}
