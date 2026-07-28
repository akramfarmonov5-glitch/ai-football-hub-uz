import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { AlertTriangle } from "lucide-react";
import { getMeta } from "../lib/server-api";
import { SearchModal } from "../components/SearchModal";

/**
 * Shrift build paytida yuklab olinadi va o'z domenimizdan beriladi.
 * Ilgari u Google serveridan `<link>` orqali olinardi: har bir tashrifda
 * tashqi so'rov, sekinroq yuklanish va matn sakrashi (CLS) bo'lardi.
 *
 * Outfit — variable shrift, shuning uchun `weight` ko'rsatilmaydi: barcha
 * qalinliklar (300-800) bitta fayldan keladi.
 */
const outfit = Outfit({
  subsets: ["latin", "latin-ext"],
  display: "swap",
  variable: "--font-outfit",
});

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";
const TELEGRAM_BOT_URL =
  process.env.NEXT_PUBLIC_TELEGRAM_BOT_URL ?? "https://t.me/";

const SITE_NAME = "AI Football Hub Uzbekistan";
const SITE_DESCRIPTION =
  "O'zbekistondagi birinchi to'liq sun'iy intellekt orqali ishlovchi futbol platformasi. Jonli hisoblar, o'yinoldi va o'yindan keyingi tahlillar.";

export const metadata: Metadata = {
  // Nisbiy URL'lar (og:url, canonical) shu manzilga nisbatan to'ldiriladi
  metadataBase: new URL(SITE_URL),
  title: {
    default: `${SITE_NAME} - Live Natijalar va AI Tahlil`,
    // Ichki sahifalar o'z sarlavhasini beradi, oxiriga sayt nomi qo'shiladi
    template: `%s | ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,
  applicationName: SITE_NAME,
  openGraph: {
    type: "website",
    siteName: SITE_NAME,
    locale: "uz_UZ",
    title: `${SITE_NAME} - Live Natijalar va AI Tahlil`,
    description: SITE_DESCRIPTION,
    url: "/",
  },
  twitter: {
    card: "summary_large_image",
    title: `${SITE_NAME} - Live Natijalar va AI Tahlil`,
    description: SITE_DESCRIPTION,
  },
  // `robots` ataylab belgilanmagan: teg bo'lmasa indeksatsiya baribir ruxsat
  // etilgan. Aksincha, uni yozib qo'ysak, Next.js topilmagan sahifalarga
  // avtomatik qo'yadigan `noindex` bilan qarama-qarshi teg paydo bo'lardi.
  alternates: { canonical: "/" },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Bitta joyda so'raladi va banner bilan footer ikkalasida ishlatiladi —
  // ular bir-biriga zid gapirmasligi kerak (banner "demo" desa-yu, footer
  // "haqiqiy" desa, chalkashlik chiqardi).
  const meta = await getMeta();

  return (
    <html lang="uz" className={`${outfit.variable} h-full dark`}>
      <body className="min-h-full flex flex-col bg-[#060913] text-slate-100 font-sans selection:bg-cyan-500 selection:text-black">
        {/* Ma'lumot manbai haqiqiy bo'lmasa — har bir sahifada ogohlantiramiz */}
        {meta.is_simulated && (
          <div
            role="status"
            className="w-full bg-amber-500/10 border-b border-amber-500/25 text-amber-300"
          >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5 flex items-start gap-2 text-xs">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-px" />
              <p className="leading-relaxed">
                <strong className="font-bold">Demo rejimi.</strong> Bu
                sahifadagi o'yinlar, hisoblar va turnir jadvali{" "}
                <strong>haqiqiy emas</strong> — ular namoyish uchun avtomatik
                yaratilgan. Haqiqiy natijalar uchun API-Football kaliti
                ulanishi kerak.
              </p>
            </div>
          </div>
        )}

        <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-[#060913]/80 backdrop-blur-md">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-8">
              <Link href="/" className="flex items-center space-x-2">
                <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                  AI FOOTBALL HUB
                </span>
                <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded-full font-bold">
                  UZB
                </span>
              </Link>
              <nav className="hidden md:flex space-x-6 text-sm font-medium text-slate-300">
                <Link href="/#match-center" className="hover:text-emerald-400 transition-colors">
                  Match Markazi
                </Link>
                <Link href="/standings" className="hover:text-emerald-400 transition-colors">
                  Turnir jadvali
                </Link>
                <Link href="/#news-section" className="hover:text-emerald-400 transition-colors">
                  Yangiliklar
                </Link>
              </nav>
            </div>

            <div className="flex items-center space-x-3">
              <SearchModal />
              <a
                href={TELEGRAM_BOT_URL}
                target="_blank"
                rel="noreferrer"
                className="bg-sky-500 hover:bg-sky-600 text-white text-xs font-semibold px-4 py-2 rounded-full transition-colors shadow-lg shadow-sky-500/10"
              >
                Telegram Bot 🤖
              </a>
            </div>
          </div>
        </header>

        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        <footer className="border-t border-white/5 py-8 mt-12 bg-[#04060d]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-slate-500">
            <p>© {new Date().getFullYear()} {SITE_NAME}. Barcha huquqlar himoyalangan.</p>
            <p className="mt-2 text-slate-600">
              {meta.is_simulated ? (
                <>
                  Demo rejimida o'yinlar, hisoblar va turnir jadvali namoyish
                  uchun avtomatik yaratiladi — ular haqiqiy uchrashuvlarni aks
                  ettirmaydi.{" "}
                </>
              ) : (
                <>Natijalar tashqi manbalardan avtomatik yangilanib turadi. </>
              )}
              AI tahlillari sun'iy intellekt tomonidan generatsiya qilinadi.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
