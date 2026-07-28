"use client";

import { useState, useEffect } from "react";

/**
 * O'yingacha qolgan vaqtni hisoblaydi va ko'rsatadi.
 * match_time ISO formatda kelishi kerak.
 */
export function MatchCountdown({ matchTime }: { matchTime: string }) {
  const [timeLeft, setTimeLeft] = useState<string>("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);

    const calc = () => {
      const now = Date.now();
      const target = new Date(matchTime).getTime();
      const diff = target - now;

      if (diff <= 0) {
        setTimeLeft("");
        return;
      }

      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      if (days > 0) {
        setTimeLeft(`${days}k ${hours}s ${minutes}d`);
      } else if (hours > 0) {
        setTimeLeft(`${hours}s ${minutes}d ${seconds}s`);
      } else {
        setTimeLeft(`${minutes}d ${seconds}s`);
      }
    };

    calc();
    const interval = setInterval(calc, 1000);
    return () => clearInterval(interval);
  }, [matchTime]);

  if (!mounted || !timeLeft) return null;

  return (
    <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-center space-x-2">
      <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Boshlanishga:</span>
      <div className="flex items-center space-x-1">
        {timeLeft.split(" ").map((part, idx) => (
          <span
            key={idx}
            className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-black px-1.5 py-0.5 rounded-md tracking-wider"
          >
            {part}
          </span>
        ))}
      </div>
    </div>
  );
}
