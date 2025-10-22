/**
 * Tiny auth helper for browser-side JWT handling.
 * Stores a bearer token in localStorage under TOKEN_KEY.
 *
 * Note: In this prototype we call backend via /api/proxy and
 * add the Authorization header from the browser. You can swap
 * this with proper NextAuth/Passport later.
 */

const TOKEN_KEY = "io_jwt";

export function setToken(token: string) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
}

// Convenience helpers you can use on client components
export async function login(email: string, password: string) {
  const res = await fetch("/api/proxy/users/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  setToken(data.access_token);
  return data;
}

export async function signup(email: string, password: string) {
  const res = await fetch("/api/proxy/users/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  setToken(data.access_token);
  return data;
}

export async function me() {
  const token = getToken();
  const res = await fetch("/api/proxy/users/me", {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ email: string; role: string }>;
}
