/**
 * SentinelMesh API & WebSocket Configuration
 * Dynamically resolves production vs development endpoints.
 * Supports:
 * 1. Unified server (FastAPI serving Vite dist on the same host & port)
 * 2. Decoupled deployment (Vercel frontend pointing to Render/Railway backend via VITE_API_URL)
 * 3. Local development (Vite on :5173 proxying or calling backend on :8000)
 */

const getApiBase = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL.replace(/\/$/, "");
  }
  if (typeof window !== "undefined") {
    // If running in browser on port 5173 (Vite dev), default to port 8000
    if (window.location.port === "5173") {
      return "http://localhost:8000";
    }
    // In production unified server, use current origin
    return window.location.origin;
  }
  return "http://localhost:8000";
};

const getWsBase = () => {
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL.replace(/\/$/, "");
  }
  if (typeof window !== "undefined") {
    if (window.location.port === "5173") {
      return "ws://localhost:8000";
    }
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}`;
  }
  return "ws://localhost:8000";
};

export const API_BASE = getApiBase();
export const WS_BASE = getWsBase();
