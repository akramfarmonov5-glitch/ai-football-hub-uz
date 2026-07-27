"use client";

import { useEffect, useRef, useState } from "react";
import { getLocalMatches, getLocalNews, simulateLocalTick } from "./mockStore";
import type { Match, NewsItem } from "./types";
import { apiUrl, WS_URL } from "./api";

/** Qayta ulanish oralig'i: 1s, 2s, 4s ... maksimum 30s */
const RECONNECT_BASE_MS = 1000;
const RECONNECT_MAX_MS = 30000;

interface Options {
  /** Serverda yuklangan boshlang'ich ma'lumot (SSR) */
  initialMatches?: Match[];
  initialNews?: NewsItem[];
}

/**
 * Jonli yangilanishlarni boshqaradi.
 *
 * Boshlang'ich ma'lumot serverdan props orqali keladi, shuning uchun sahifa
 * darhol to'liq ko'rinadi. Keyin WebSocket orqali hisoblar yangilanib turadi.
 * Ulanish uzilsa avtomatik tiklanadi; backend umuman yo'q bo'lsa brauzerdagi
 * demo ma'lumotlarga o'tiladi.
 */
export function useMatches({ initialMatches = [], initialNews = [] }: Options = {}) {
  const [matches, setMatches] = useState<Match[]>(initialMatches);
  const [news, setNews] = useState<NewsItem[]>(initialNews);
  const [loading, setLoading] = useState(initialMatches.length === 0);
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
          // Serverdagi getMatches bilan bir xil oyna (lib/server-api.ts)
          fetch(apiUrl("/matches/?days=2&limit=100")),
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

    // Server allaqachon ma'lumot bergan bo'lsa, darhol qayta so'ramaymiz —
    // WebSocket yangilanishlarni o'zi olib keladi.
    if (initialMatches.length === 0) fetchData();

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { matches, news, loading, isOffline };
}

/**
 * Bitta o'yinni jonli kuzatadi (o'yin sahifasi uchun).
 * Boshlang'ich qiymat serverdan keladi.
 */
export function useLiveMatch(initialMatch: Match) {
  const [match, setMatch] = useState<Match>(initialMatch);

  useEffect(() => {
    let closedByUs = false;
    let attempts = 0;
    let socket: WebSocket | null = null;
    let timer: ReturnType<typeof setTimeout> | null = null;

    function connect() {
      if (closedByUs) return;
      socket = new WebSocket(WS_URL);

      socket.onopen = () => {
        attempts = 0;
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event === "match_update" && data.match.id === initialMatch.id) {
            setMatch((prev) => ({ ...prev, ...data.match }));
          }
        } catch (err) {
          console.error(err);
        }
      };

      socket.onclose = () => {
        if (closedByUs) return;
        const delay = Math.min(RECONNECT_BASE_MS * 2 ** attempts, RECONNECT_MAX_MS);
        attempts += 1;
        timer = setTimeout(connect, delay);
      };
    }
    connect();

    return () => {
      closedByUs = true;
      if (timer) clearTimeout(timer);
      socket?.close();
    };
  }, [initialMatch.id]);

  return match;
}
