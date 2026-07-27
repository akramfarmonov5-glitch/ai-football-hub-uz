"use client";

import { useState } from "react";
import { Share2, Check } from "lucide-react";

/** Havolani nusxalaydi. Sahifaning yagona interaktiv qismi bo'lgani uchun
 *  alohida klient komponent — qolgan maqola serverda render qilinadi. */
export function ShareButton() {
  const [copied, setCopied] = useState(false);

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard ruxsati yo'q (masalan HTTPS bo'lmagan muhitda)
      console.warn("Havolani nusxalab bo'lmadi");
    }
  };

  return (
    <button
      onClick={handleShare}
      className="hover:text-cyan-400 flex items-center transition-colors cursor-pointer"
      aria-label="Havolani nusxalash"
    >
      {copied ? (
        <>
          <Check className="w-3.5 h-3.5 mr-1 text-emerald-400" />
          Nusxalandi
        </>
      ) : (
        <>
          <Share2 className="w-3.5 h-3.5 mr-1" />
          Ulashish
        </>
      )}
    </button>
  );
}
