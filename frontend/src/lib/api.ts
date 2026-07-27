// Centralized API / WebSocket endpoints.
// Override per environment via .env.local (see .env.local.example):
//   NEXT_PUBLIC_API_URL=https://api.example.com
//   NEXT_PUBLIC_WS_URL=wss://api.example.com/ws
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws";

// Build a full API URL for a path like "/matches/" or `/news/${slug}`.
export const apiUrl = (path: string) => `${API_BASE_URL}/api/v1${path}`;
