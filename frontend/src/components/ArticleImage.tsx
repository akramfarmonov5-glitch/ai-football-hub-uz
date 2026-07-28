"use client";

import { useState } from "react";
import Image from "next/image";
import { Newspaper } from "lucide-react";

export function ArticleImage({ src, title }: { src: string; title: string }) {
  const [error, setError] = useState(false);

  if (error || !src) {
    return (
      <div className="relative aspect-video rounded-3xl overflow-hidden border border-white/10 bg-gradient-to-br from-slate-900 via-cyan-950/40 to-slate-950 flex flex-col items-center justify-center p-6 text-center space-y-3">
        <Newspaper className="w-12 h-12 text-cyan-400/60" />
        <span className="text-sm font-bold text-slate-300 max-w-md line-clamp-2">{title}</span>
      </div>
    );
  }

  return (
    <div className="relative aspect-video rounded-3xl overflow-hidden border border-white/10 bg-slate-950">
      <Image
        src={src}
        alt={title}
        fill
        sizes="(max-width: 768px) 100vw, 768px"
        className="object-cover"
        onError={() => setError(true)}
        unoptimized
      />
    </div>
  );
}
