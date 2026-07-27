import { AlertTriangle } from "lucide-react";
import { getMeta } from "../lib/server-api";

/**
 * Simulyatsiya rejimida saytning har bir sahifasida ko'rinadigan ogohlantirish.
 *
 * Nima uchun kerak: simulyator haqiqiy jamoa nomlari bilan o'yin va hisoblarni
 * o'zi to'qib chiqaradi. Ogohlantirishsiz tashrif buyuruvchi "Liverpool 1-0
 * Arsenal" ni bugungi haqiqiy natija deb qabul qiladi. Manba ko'rsatilmasa
 * sayt yolg'on ma'lumot tarqatgan bo'ladi.
 */
export async function SimulationNotice() {
  const meta = await getMeta();
  if (!meta.is_simulated) return null;

  return (
    <div
      role="status"
      className="w-full bg-amber-500/10 border-b border-amber-500/25 text-amber-300"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5 flex items-start gap-2 text-xs">
        <AlertTriangle className="w-4 h-4 shrink-0 mt-px" />
        <p className="leading-relaxed">
          <strong className="font-bold">Demo rejimi.</strong> Bu sahifadagi
          o'yinlar, hisoblar va turnir jadvali <strong>haqiqiy emas</strong> —
          ular namoyish uchun avtomatik yaratilgan. Haqiqiy natijalar uchun
          API-Football kaliti ulanishi kerak.
        </p>
      </div>
    </div>
  );
}
