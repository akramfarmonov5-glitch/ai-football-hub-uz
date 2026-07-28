"use client";

import Link from "next/link";
import { Newspaper, ChevronRight } from "lucide-react";
import type { NewsItem } from "../lib/types";
import { formatDate } from "../lib/time";

export function NewsList({ news }: { news: NewsItem[] }) {
  return (
    <div id="news-section" className="flex flex-col justify-between space-y-6">
      <div className="flex items-center justify-between border-b border-white/5 pb-4">
        <h2 className="text-lg font-black flex items-center space-x-2">
          <Newspaper className="w-5 h-5 text-cyan-400" />
          <span>Qaynoq Xabarlar</span>
        </h2>
      </div>

      <div className="flex-1 space-y-4 max-h-[360px] overflow-y-auto pr-1">
        {news.map((item) => (
          <Link
            key={item.id}
            href={`/news/${item.slug}`}
            className="block glass-panel p-4 rounded-2xl hover:scale-[1.01] transition-transform duration-200 hover:border-cyan-500/20"
          >
            <div className="space-y-2">
              <div className="flex flex-wrap gap-1.5">
                {item.tags?.map((t) => {
                  const cleanTag = t.replace(/^#+/, "");
                  return (
                    <span key={t} className="text-[9px] bg-cyan-500/10 text-cyan-400 border border-cyan-500/10 px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">
                      #{cleanTag}
                    </span>
                  );
                })}
              </div>
              <h3 className="text-sm font-bold line-clamp-2 hover:text-cyan-300 transition-colors">
                {item.title}
              </h3>
              <p className="text-xs text-slate-400 line-clamp-2">
                {item.summary}
              </p>
              <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 font-medium">
                <span>{formatDate(item.created_at)}</span>
                <span className="flex items-center text-cyan-400 hover:underline">
                  O'qish <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
