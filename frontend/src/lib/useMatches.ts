"use client";

import { useEffect, useState } from "react";
import {
  getLocalMatches,
  getLocalNews,
  simulateLocalTick,
  Match,
  NewsItem,
} from "./mockStore";
import { apiUrl, WS_URL } from "./api";

/**
 * Loads matches + news, subscribes to live WebSocket updates, and falls back
 * to the local mock store (with a client-side ticker) when the backend is offline.
 */
export function useMatches() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const matchesRes = await fetch(apiUrl("/matches/"));
        const newsRes = await fetch(apiUrl("/news/"));
        if (matchesRes.ok) {
          setMatches(await matchesRes.json());
          setIsOffline(false);
        } else {
          throw new Error("API error");
        }
        if (newsRes.ok) setNews(await newsRes.json());
      } catch (err) {
        console.warn("Backend offline, loading localStorage mocks.");
        setIsOffline(true);
        setMatches(getLocalMatches());
        setNews(getLocalNews());
      } finally {
        setLoading(false);
      }
    }
    fetchData();

    // Live updates over WebSocket
    const socket = new WebSocket(WS_URL);
    socket.onopen = () => setIsOffline(false);
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

    // Offline fallback ticker
    const clientSimulationInterval = setInterval(() => {
      if (socket.readyState !== WebSocket.OPEN) {
        setMatches(simulateLocalTick());
      }
    }, 4000);

    return () => {
      socket.close();
      clearInterval(clientSimulationInterval);
    };
  }, []);

  return { matches, news, loading, isOffline };
}
