import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center space-y-4">
      <span className="text-6xl font-black text-slate-800">404</span>
      <h1 className="text-xl font-bold">Sahifa topilmadi</h1>
      <p className="text-sm text-slate-400 max-w-sm">
        Siz qidirayotgan sahifa mavjud emas yoki o'chirilgan bo'lishi mumkin.
      </p>
      <Link
        href="/"
        className="inline-flex items-center text-emerald-400 hover:text-emerald-300 text-sm font-semibold"
      >
        <ArrowLeft className="w-4 h-4 mr-2" /> Bosh sahifaga qaytish
      </Link>
    </div>
  );
}
