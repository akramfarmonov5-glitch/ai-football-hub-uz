"use client";

import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Sahifada xato:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center space-y-4">
      <AlertTriangle className="w-10 h-10 text-amber-400" />
      <h1 className="text-xl font-bold">Nimadir noto'g'ri ketdi</h1>
      <p className="text-sm text-slate-400 max-w-sm">
        Sahifani yuklashda xatolik yuz berdi. Qayta urinib ko'ring — muammo
        takrorlansa, server ishlayotganini tekshiring.
      </p>
      <button
        onClick={reset}
        className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold px-5 py-2 rounded-xl text-xs cursor-pointer"
      >
        Qayta urinish
      </button>
    </div>
  );
}
