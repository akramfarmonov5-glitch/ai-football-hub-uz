"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { ArrowLeft, Calendar, Tag, Share2, Globe } from "lucide-react";
import { getLocalNews, NewsItem } from "../../../lib/mockStore";
import { apiUrl } from "../../../lib/api";

export default function NewsDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const resolvedParams = use(params);
  const slug = resolvedParams.slug;
  const [news, setNews] = useState<NewsItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchNews() {
      try {
        const res = await fetch(apiUrl(`/news/${slug}`));
        if (res.ok) {
          setNews(await res.json());
        } else {
          throw new Error("News detail API error");
        }
      } catch (err) {
        console.warn("Backend offline, loading news from local mock store.");
        const newsList = getLocalNews();
        const found = newsList.find(n => n.slug === slug);
        if (found) setNews(found);
      } finally {
        setLoading(false);
      }
    }
    fetchNews();
  }, [slug]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <div className="w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 font-medium">Yangilik yuklanmoqda...</p>
      </div>
    );
  }

  if (!news) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-bold">Maqola topilmadi</h2>
        <Link href="/" className="text-cyan-400 inline-flex items-center mt-4">
          <ArrowLeft className="w-4 h-4 mr-2" /> Match markaziga qaytish
        </Link>
      </div>
    );
  }

  return (
    <article className="max-w-3xl mx-auto space-y-8">
      <Link href="/" className="inline-flex items-center text-slate-400 hover:text-cyan-400 text-sm transition-colors">
        <ArrowLeft className="w-4 h-4 mr-2" /> Orqaga qaytish
      </Link>

      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          {news.tags?.map((t) => (
            <span key={t} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/25">
              <Tag className="w-3 h-3 mr-1" />
              {t}
            </span>
          ))}
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-100 leading-tight">
          {news.title}
        </h1>
        
        <div className="flex items-center justify-between text-xs text-slate-500 border-y border-white/5 py-3">
          <span className="flex items-center">
            <Calendar className="w-3.5 h-3.5 mr-1" />
            {new Date(news.created_at).toLocaleDateString("uz-UZ", {
              year: "numeric",
              month: "long",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit"
            })}
          </span>
          <div className="flex space-x-4">
            <button 
              onClick={() => {
                navigator.clipboard.writeText(window.location.href);
                alert("Havola nusxalandi!");
              }}
              className="hover:text-cyan-400 flex items-center transition-colors cursor-pointer"
            >
              <Share2 className="w-3.5 h-3.5 mr-1" />
              Ulashish
            </button>
          </div>
        </div>
      </div>

      {news.image_url && (
        <div className="relative aspect-video rounded-3xl overflow-hidden border border-white/5">
          <img src={news.image_url} alt={news.title} className="object-cover w-full h-full" />
        </div>
      )}

      {news.summary && (
        <div className="p-5 rounded-2xl bg-slate-900/50 border-l-4 border-cyan-500 text-slate-300 text-sm leading-relaxed italic">
          {news.summary}
        </div>
      )}

      <div className="prose prose-invert prose-cyan max-w-none text-slate-300 leading-relaxed text-sm md:text-base space-y-6 whitespace-pre-line">
        {news.content}
      </div>

      {news.source_url && (
        <div className="pt-6 border-t border-white/5 flex items-center">
          <Globe className="w-4 h-4 text-slate-500 mr-2" />
          <span className="text-xs text-slate-500">Asl manba: </span>
          <a href={news.source_url} target="_blank" rel="noreferrer" className="text-xs text-cyan-400 ml-1.5 hover:underline font-medium">
            {news.source_url}
          </a>
        </div>
      )}
    </article>
  );
}
