"use client";

import Link from "next/link";
import Image from "next/image";
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

      <div className="flex-1 space-y-4 max-h-[460px] overflow-y-auto pr-1 stagger-children">
        {news.length === 0 && (
          <p className="text-xs text-slate-500 text-center py-8">
            Hozircha yangilik yo'q.
          </p>
        )}
        {news.map((item) => {
          const cleanTag = (t: string) => t.replace(/^#+/, "");
          return (
            <Link
              key={item.id}
              href={`/news/${item.slug}`}
              className="block glass-panel rounded-2xl overflow-hidden hover:scale-[1.01] transition-transform duration-200 hover:border-cyan-500/20"
            >
              {/* Rasm bo'limi */}
              {item.image_url ? (
                <div className="relative w-full h-36 bg-slate-900">
                  <Image
                    src={item.image_url}
                    alt={item.title}
                    fill
                    sizes="(max-width: 768px) 100vw, 400px"
                    className="object-cover"
                    unoptimized
                  />
                  {/* Gradient overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-950/30 to-transparent" />
                  {/* Tags on image */}
                  <div className="absolute bottom-2 left-3 flex flex-wrap gap-1">
                    {item.tags?.slice(0, 2).map((t) => (
                      <span
                        key={t}
                        className="text-[8px] bg-cyan-500/30 text-cyan-200 backdrop-blur-sm px-2 py-0.5 rounded-full font-bold uppercase tracking-wider"
                      >
                        #{cleanTag(t)}
                      </span>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="relative w-full h-28 bg-gradient-to-br from-cyan-950/40 via-slate-900 to-slate-950 flex items-center justify-center">
                  <Newspaper className="w-8 h-8 text-cyan-500/30" />
                  <div className="absolute bottom-2 left-3 flex flex-wrap gap-1">
                    {item.tags?.slice(0, 2).map((t) => (
                      <span
                        key={t}
                        className="text-[8px] bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded-full font-bold uppercase tracking-wider"
                      >
                        #{cleanTag(t)}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Matn bo'limi */}
              <div className="p-4 space-y-2">
                <h3 className="text-sm font-bold line-clamp-2 hover:text-cyan-300 transition-colors leading-snug">
                  {item.title}
                </h3>
                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
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
          );
        })}
      </div>
    </div>
  );
}
