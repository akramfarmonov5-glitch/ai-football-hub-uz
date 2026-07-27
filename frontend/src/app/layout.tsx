import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";

export const metadata: Metadata = {
  title: "AI Football Hub Uzbekistan - Live Natijalar va AI Tahlil",
  description: "O'zbekistondagi birinchi to'liq sun'iy intellekt orqali ishlovchi futbol platformasi. Jonli hisoblar, o'yinoldi va o'yindan keyingi tahlillar.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="uz" className="h-full dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body className="min-h-full flex flex-col bg-[#060913] text-slate-100 font-sans selection:bg-cyan-500 selection:text-black">
        {/* Navigation Header */}
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
                <Link href="/#news-section" className="hover:text-emerald-400 transition-colors">
                  Yangiliklar
                </Link>
              </nav>
            </div>
            
            <div className="flex items-center space-x-4">
              <a 
                href="https://t.me/your_bot_username" 
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
            <p>© {new Date().getFullYear()} AI Football Hub Uzbekistan. Barcha huquqlar himoyalangan.</p>
            <p className="mt-2 text-slate-600">Loyiha test rejimida ishlamoqda. AI tahlillari sun'iy intellekt tomonidan generatsiya qilinadi.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
