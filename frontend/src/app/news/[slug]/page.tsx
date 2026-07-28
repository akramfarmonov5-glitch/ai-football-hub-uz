import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { notFound } from "next/navigation";
import { cache } from "react";
import { ArrowLeft, Calendar, Tag, Globe } from "lucide-react";

import { getNewsArticle } from "../../../lib/server-api";
import { formatDateTime } from "../../../lib/time";
import { ShareButton } from "../../../components/ShareButton";
import { NewsComments } from "../../../components/NewsComments";

type Props = { params: Promise<{ slug: string }> };

const loadArticle = cache(getNewsArticle);

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const news = await loadArticle(slug);

  if (!news) {
    return { title: "Maqola topilmadi" };
  }

  const description =
    news.summary?.slice(0, 160) ||
    news.content.replace(/[*#]/g, "").slice(0, 160);

  return {
    title: news.title,
    description,
    keywords: news.tags,
    openGraph: {
      title: news.title,
      description,
      type: "article",
      publishedTime: news.created_at,
      tags: news.tags,
      url: `/news/${news.slug}`,
      images: news.image_url ? [{ url: news.image_url }] : undefined,
    },
    twitter: {
      card: news.image_url ? "summary_large_image" : "summary",
      title: news.title,
      description,
    },
    alternates: { canonical: `/news/${news.slug}` },
  };
}

export default async function NewsDetailPage({ params }: Props) {
  const { slug } = await params;
  const news = await loadArticle(slug);

  if (!news) notFound();

  return (
    <article className="max-w-3xl mx-auto space-y-8">
      <Link
        href="/"
        className="inline-flex items-center text-slate-400 hover:text-cyan-400 text-sm transition-colors"
      >
        <ArrowLeft className="w-4 h-4 mr-2" /> Orqaga qaytish
      </Link>

      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          {news.tags?.map((t) => (
            <span
              key={t}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/25"
            >
              <Tag className="w-3 h-3 mr-1" />
              {t}
            </span>
          ))}
        </div>

        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-100 leading-tight">
          {news.title}
        </h1>

        <div className="flex items-center justify-between text-xs text-slate-500 border-y border-white/5 py-3">
          <time dateTime={news.created_at} className="flex items-center">
            <Calendar className="w-3.5 h-3.5 mr-1" />
            {formatDateTime(news.created_at)}
          </time>
          <div className="flex space-x-4">
            <ShareButton />
          </div>
        </div>
      </div>

      {news.image_url && (
        <div className="relative aspect-video rounded-3xl overflow-hidden border border-white/5">
          <Image
            src={news.image_url}
            alt={news.title}
            fill
            sizes="(max-width: 768px) 100vw, 768px"
            className="object-cover"
            unoptimized
          />
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
          <a
            href={news.source_url}
            target="_blank"
            rel="noreferrer"
            className="text-xs text-cyan-400 ml-1.5 hover:underline font-medium"
          >
            {news.source_url}
          </a>
        </div>
      )}

      <NewsComments newsSlug={news.slug} />
    </article>
  );
}
