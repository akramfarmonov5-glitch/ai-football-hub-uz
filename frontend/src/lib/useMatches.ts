"use client";

import { useEffect, useRef, useState } from "react";
import {
  getLocalMatches,
  getLocalNews,
  simulateLocalTick,
  Match,
  NewsItem,
} from "./mockStore";
import { apiUrl, WS_URL } from "./api";

/** Qayta ulanish oralig'i: 1s, 2s, 4s ... maksimum 30s */
const RECONNECT_BASE_MS = 1000;
const RECONNECT_MAX_MS = 30000;

/**
 * O'yinlar va yangiliklarni yuklaydi, WebSocket orqali jonli yangilanishlarga
 * obuna bo'ladi, backend ishlamasa lokal demo ma'lumotlarga o'tadi.
 *
 * Ilgari WebSocket uzilib qolsa hech narsa qilinmasdi: sayt jimgina eskirgan
 * hisobni ko'rsatib turaverardi va "offline" belgisi ham chiqmasdi. Endi
 * ulanish avtomatik tiklanadi va holat foydalanuvchiga to'g'ri ko'rsatiladi.
 */
export function useMatches() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isOffline, setIsOffline] = useState(false);

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const attemptsRef = useRef(0);
  const closedByUsRef = useRef(false);
  // Backend hech qachon javob bermadimi? Faqat shu holatda lokal demo ishlaydi.
  const usingLocalDataRef = useRef(false);

  useEffect(() => {
    closedByUsRef.current = false;

    async function fetchData() {
      try {
        const [matchesRes, newsRes] = await Promise.all([
          fetch(apiUrl("/matches/")),
          fetch(apiUrl("/news/")),
        ]);
        if (!matchesRes.ok) throw new Error("API error");

        setMatches(await matchesRes.json());
        usingLocalDataRef.current = false;
        setIsOffline(false);
        if (newsRes.ok) setNews(await newsRes.json());
      } catch {
        console.warn("Backend ishlamayapti — lokal demo ma'lumotlar yuklanmoqda.");
        usingLocalDataRef.current = true;
        setIsOffline(true);
        setMatches(getLocalMatches());
        setNews(getLocalNews());
      } finally {
        setLoading(false);
      }
    }
    fetchData();

    function connect() {
      if (closedByUsRef.current) return;

      const socket = new WebSocket(WS_URL);
      socketRef.current = socket;

      socket.onopen = () => {
        // Uzilib qolgan vaqtdagi yangilanishlarni o'tkazib yubormaslik uchun
        // qayta ulangach ma'lumotni to'liq yangilaymiz.
        if (attemptsRef.current > 0) fetchData();
        attemptsRef.current = 0;
        setIsOffline(false);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event === "match_update") {
            setMatches((prev) =>
              prev.map((m) => (m.id === data.match.id ? { ...m, ...data.match } : m))
            );
          }
        } catch (err) {
          console.error(err);
        }
      };

      // Uzilish — brauzer `onerror` dan keyin har doim `onclose` ni chaqiradi,
      // shuning uchun qayta ulanishni faqat shu yerda boshqaramiz.
      socket.onclose = () => {
        if (closedByUsRef.current) return;
        setIsOffline(true);

        const delay = Math.min(
          RECONNECT_BASE_MS * 2 ** attemptsRef.current,
          RECONNECT_MAX_MS
        );
        attemptsRef.current += 1;
        reconnectTimerRef.current = setTimeout(connect, delay);
      };
    }
    connect();

    // Zaxira ticker — faqat backend umuman yo'q bo'lganda ishlaydi.
    // Aks holda WebSocket qisqa uzilganda haqiqiy hisob demo ma'lumot bilan
    // almashtirilib yuborilardi.
    const localTicker = setInterval(() => {
      if (usingLocalDataRef.current) {
        setMatches(simulateLocalTick());
      }
    }, 4000);

    return () => {
      closedByUsRef.current = true;
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      socketRef.current?.close();
      clearInterval(localTicker);
    };
  }, []);

  return { matches, news, loading, isOffline };
}
