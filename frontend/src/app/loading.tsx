/** Sahifa ma'lumoti yuklanayotganda ko'rsatiladi (Next.js streaming). */
export default function Loading() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
      <div className="w-8 h-8 border-4 border-emerald-400 border-t-transparent rounded-full animate-spin" />
      <p className="text-slate-400 text-sm">Yuklanmoqda...</p>
    </div>
  );
}
