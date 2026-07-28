import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { AlertTriangle, Tv, Newspaper, Table2, Send } from "lucide-react";
import { getMeta } from "../lib/server-api";
import { SearchModal } from "../components/SearchModal";
import { FavoriteTeamPicker } from "../components/FavoriteTeamPicker";
import { MobileMenu } from "../components/MobileMenu";

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
  "O'zbekistonning eng yaxshi futbol platformasi. Jonli hisoblar, o'yinoldi va o'yindan keyingi ekspert tahlillari.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: `${SITE_NAME} - Jonli Natijalar va Ekspert Tahlil`,
    template: `%s | ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,
  applicationName: SITE_NAME,
  openGraph: {
    type: "website",
    siteName: SITE_NAME,
    locale: "uz_UZ",
    title: `${SITE_NAME} - Jonli Natijalar va Ekspert Tahlil`,
    description: SITE_DESCRIPTION,
    url: "/",
  },
  twitter: {
    card: "summary_large_image",
    title: `${SITE_NAME} - Jonli Natijalar va Ekspert Tahlil`,
    description: SITE_DESCRIPTION,
  },
  manifest: "/manifest.json",
  alternates: { canonical: "/" },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const meta = await getMeta();

  return (
    <html lang="uz" className={`${outfit.variable} h-full dark`}>
      <body className="min-h-full flex flex-col bg-[#060913] text-slate-100 font-sans selection:bg-cyan-500 selection:text-black">
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
                  O'yin Markazi
                </Link>
                <Link href="/standings" className="hover:text-emerald-400 transition-colors">
                  Turnir jadvali
                </Link>
                <Link href="/#news-section" className="hover:text-emerald-400 transition-colors">
                  Yangiliklar
                </Link>
              </nav>
            </div>

            <div className="flex items-center space-x-2.5">
              <SearchModal />
              <FavoriteTeamPicker />
              <a
                href={TELEGRAM_BOT_URL}
                target="_blank"
                rel="noreferrer"
                className="hidden sm:inline-flex bg-sky-500 hover:bg-sky-600 text-white text-xs font-semibold px-4 py-2 rounded-full transition-colors shadow-lg shadow-sky-500/10"
              >
                Telegram Bot 🤖
              </a>
              <MobileMenu />
            </div>
          </div>
        </header>

        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        {/* ===== Professional Footer ===== */}
        <footer className="border-t border-white/5 bg-[#04060d]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-10 md:gap-8">
              {/* Logo + ta'rif */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <span className="text-lg font-extrabold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                    AI FOOTBALL HUB
                  </span>
                  <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded-full font-bold">
                    UZB
                  </span>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed max-w-xs">
                  O'zbekistonning eng yaxshi futbol
                  platformasi. Jonli natijalar, ekspert prognozlari va yangiliklar.
                </p>
              </div>

              {/* Tezkor havolalar */}
              <div className="space-y-4">
                <h4 className="text-xs font-extrabold text-slate-300 uppercase tracking-wider">
                  Tezkor Havolalar
                </h4>
                <nav className="flex flex-col space-y-2.5">
                  <Link href="/" className="text-xs text-slate-500 hover:text-emerald-400 transition-colors flex items-center space-x-2">
                    <Tv className="w-3 h-3" /><span>Bosh sahifa</span>
                  </Link>
                  <Link href="/#match-center" className="text-xs text-slate-500 hover:text-emerald-400 transition-colors flex items-center space-x-2">
                    <Tv className="w-3 h-3" /><span>O'yin Markazi</span>
                  </Link>
                  <Link href="/standings" className="text-xs text-slate-500 hover:text-emerald-400 transition-colors flex items-center space-x-2">
                    <Table2 className="w-3 h-3" /><span>Turnir jadvali</span>
                  </Link>
                  <Link href="/#news-section" className="text-xs text-slate-500 hover:text-emerald-400 transition-colors flex items-center space-x-2">
                    <Newspaper className="w-3 h-3" /><span>Yangiliklar</span>
                  </Link>
                </nav>
              </div>

              {/* Ijtimoiy tarmoqlar */}
              <div className="space-y-4">
                <h4 className="text-xs font-extrabold text-slate-300 uppercase tracking-wider">
                  Biz bilan bog'laning
                </h4>
                <div className="flex flex-col space-y-2.5">
                  <a
                    href="https://t.me/aifootball_uz"
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-slate-500 hover:text-sky-400 transition-colors flex items-center space-x-2"
                  >
                    <Send className="w-3 h-3" /><span>Telegram Kanal — @aifootball_uz</span>
                  </a>
                  <a
                    href={TELEGRAM_BOT_URL}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-slate-500 hover:text-sky-400 transition-colors flex items-center space-x-2"
                  >
                    <Send className="w-3 h-3" /><span>Telegram Bot</span>
                  </a>
                </div>
              </div>
            </div>

            {/* Pastki qator */}
            <div className="mt-10 pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-3">
              <p className="text-[10px] text-slate-600">
                © {new Date().getFullYear()} {SITE_NAME}. Barcha huquqlar himoyalangan.
              </p>
              <p className="text-[10px] text-slate-600 text-center">
                {meta.is_simulated
                  ? "Demo rejimida o'yinlar namoyish uchun avtomatik yaratiladi."
                  : "Natijalar tashqi manbalardan avtomatik yangilanib turadi."}
                {" "}Tahlillar ekspertlar tomonidan tayyorlanadi.
              </p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
