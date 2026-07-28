"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X, Trophy, Newspaper, Table2, Bot } from "lucide-react";

const TELEGRAM_BOT_URL = process.env.NEXT_PUBLIC_TELEGRAM_BOT_URL ?? "https://t.me/";

const NAV_ITEMS = [
  { href: "/#match-center", label: "O'yin Markazi", icon: Trophy },
  { href: "/standings", label: "Turnir jadvali", icon: Table2 },
  { href: "/#news-section", label: "Yangiliklar", icon: Newspaper },
];

export function MobileMenu() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Hamburger button — faqat mobilda ko'rinadi */}
      <button
        onClick={() => setIsOpen(true)}
        className="md:hidden flex items-center justify-center w-9 h-9 rounded-xl bg-white/5 border border-white/10 text-slate-300 hover:bg-white/10 transition-colors cursor-pointer"
        aria-label="Menyuni ochish"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Overlay + Slide panel */}
      {isOpen && (
        <div className="fixed inset-0 z-[999]">
          {/* Dark backdrop */}
          <div
            className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm animate-fadeIn"
            onClick={() => setIsOpen(false)}
          />

          {/* Panel */}
          <div className="absolute top-0 right-0 w-72 h-full bg-[#0a1120] border-l border-white/10 shadow-2xl animate-slideInRight flex flex-col">
            {/* Close header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
              <span className="text-sm font-extrabold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                AI FOOTBALL HUB
              </span>
              <button
                onClick={() => setIsOpen(false)}
                className="w-8 h-8 flex items-center justify-center rounded-lg bg-white/5 text-slate-400 hover:text-white cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Nav links */}
            <nav className="flex-1 px-4 py-6 space-y-2">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className="flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-semibold text-slate-300 hover:bg-emerald-500/10 hover:text-emerald-400 transition-all"
                >
                  <item.icon className="w-4 h-4 text-slate-500" />
                  <span>{item.label}</span>
                </Link>
              ))}
            </nav>

            {/* Bottom CTA */}
            <div className="px-4 pb-6 space-y-3">
              <a
                href={TELEGRAM_BOT_URL}
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-center space-x-2 bg-sky-500 hover:bg-sky-600 text-white text-xs font-bold px-4 py-3 rounded-xl transition-colors w-full"
              >
                <Bot className="w-4 h-4" />
                <span>Telegram Bot</span>
              </a>
              <p className="text-[10px] text-slate-600 text-center">
                © {new Date().getFullYear()} AI Football Hub UZB
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
