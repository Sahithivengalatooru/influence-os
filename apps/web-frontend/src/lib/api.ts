/**
 * Minimal typed client for the FastAPI backend (prototype).
 * All calls go through the Next.js proxy route (/api/proxy/*).
 *
 * - Authorization: set via localStorage token (see auth.ts).
 * - Update NEXT_PUBLIC_API_BASE_URL to point the proxy to /v1.
 */

import { getToken } from "@/lib/auth";

const BASE = "/api/proxy";

type Method = "GET" | "POST" | "PUT" | "DELETE";
type HeadersDict = Record<string, string>;

interface RequestOptions {
  auth?: boolean;
  headers?: HeadersDict;
}

function buildQS(params?: Record<string, unknown>): string {
  if (!params) return "";
  const entries = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== null && v !== ""
  );
  const s = new URLSearchParams(entries as [string, string][]).toString();
  return s ? `?${s}` : "";
}

async function request<T>(
  method: Method,
  path: string,
  body?: unknown,
  opts: RequestOptions = {}
): Promise<T> {
  const { auth = false, headers: extra = {} } = opts;

  const headers: HeadersDict = {
    "Content-Type": "application/json",
    ...extra,
  };

  if (auth) {
    const tok = getToken();
    if (tok) headers.Authorization = `Bearer ${tok}`;
  }

  const init: RequestInit = {
    method,
    headers,
  };
  if (body !== undefined && method !== "GET") {
    init.body = JSON.stringify(body);
  }

  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) {
    let msg = `${res.status} ${res.statusText}`;
    try {
      const err = await res.json();
      msg = (err?.detail as string) || msg;
    } catch {
      /* ignore non-JSON errors */
    }
    throw new Error(msg);
  }

  const ct = res.headers.get("content-type") || "";
  return (
    ct.includes("application/json") ? res.json() : (res.text() as any)
  ) as Promise<T>;
}

export const api = {
  get: <T>(path: string, opts?: RequestOptions) =>
    request<T>("GET", path, undefined, opts),
  post: <T>(path: string, body?: unknown, opts?: RequestOptions) =>
    request<T>("POST", path, body, opts),
  put: <T>(path: string, body?: unknown, opts?: RequestOptions) =>
    request<T>("PUT", path, body, opts),
  del: <T>(path: string, opts?: RequestOptions) =>
    request<T>("DELETE", path, undefined, opts),
};

/* ----------------------------- Auth ----------------------------- */

export type TokenRes = { access_token: string; token_type: "bearer" };
export type MeRes = { email: string; role: string };

export const authApi = {
  signup: (email: string, password: string) =>
    api.post<TokenRes>("/users/signup", { email, password }),
  login: (email: string, password: string) =>
    api.post<TokenRes>("/users/login", { email, password }),
  me: () => api.get<MeRes>("/users/me", { auth: true }),
  devToken: (email = "demo@example.com", role = "user", ttl_minutes = 240) =>
    api.post<TokenRes>("/auth/dev-token", { email, role, ttl_minutes }),
};

/* --------------------------- Content ---------------------------- */

export type PostType = "text" | "article" | "carousel" | "poll";
export type GenReq = {
  type: PostType;
  topic: string;
  brand_voice?: string;
  language?: string;
  n_variants?: number;
};
export type GenRes = { variants: string[] };

export const content = {
  generate: (req: GenReq) =>
    api.post<GenRes>("/content/generate", req, { auth: true }),
};

/* --------------------------- Calendar --------------------------- */

export type CalendarItem = {
  id: string;
  date: string; // YYYY-MM-DD
  title: string;
  status: "draft" | "scheduled" | "published";
};

export const calendar = {
  list: () => api.get<CalendarItem[]>("/calendar", { auth: true }),
  create: (date: string, title: string) =>
    api.post<CalendarItem>("/calendar", { date, title }, { auth: true }),
  update: (item: CalendarItem) =>
    api.put<CalendarItem>(`/calendar/${item.id}`, item, { auth: true }),
  remove: (id: string) =>
    api.del<{ ok: boolean }>(`/calendar/${id}`, { auth: true }),
};

/* ---------------------------- Trends ---------------------------- */

export const trends = {
  get: (params: { industry?: string; seed?: string } = {}) =>
    api.get<{ topics: string[] }>(`/trends${buildQS(params)}`, { auth: true }),
};

/* --------------------------- Strategy --------------------------- */

export type StrategyPlan = {
  objectives: string[];
  pillars: { name: string; description: string }[];
  cadence: { per_week: number; windows: string[] };
  kpis: string[];
  next_steps: string[];
};

export const strategy = {
  plan: () => api.post<StrategyPlan>("/strategy/plan", {}, { auth: true }),
};

/* ---------------------------- Images ---------------------------- */

export const images = {
  generate: (prompt: string, style = "minimal", size = "1024x1024") =>
    api.post<{ image_data_uri: string }>(
      "/images/generate",
      { prompt, style, size },
      { auth: true }
    ),
};

/* --------------------------- Analytics -------------------------- */

export const analytics = {
  summary: () =>
    api.get<{ ok: boolean; series: Record<string, number[]> }>(
      "/analytics/summary",
      { auth: true }
    ),
  kpi: (
    metric: "likes" | "comments" | "shares" | "ctr" | "reach",
    range_days = 7
  ) =>
    api.get<{ metric: string; values: number[] }>(
      `/analytics/kpi${buildQS({ metric, range_days })}`,
      { auth: true }
    ),
};

/* --------------------------- Hashtags --------------------------- */

export const hashtags = {
  suggest: (topic: string) =>
    api.post<{ hashtags: string[] }>(
      "/hashtags/suggest",
      { topic },
      { auth: true }
    ),
};

/* ---------------------------- A/B Tests ------------------------- */

export type Experiment = {
  id: string;
  name: string;
  goal: string;
  status: "draft" | "running" | "stopped";
  a: string;
  b: string;
  winner?: string | null;
};

export const abtests = {
  create: (name: string, goal: string, a: string, b: string) =>
    api.post<Experiment>("/abtests", { name, goal, a, b }, { auth: true }),
  get: (exp_id: string) =>
    api.get<Experiment>(`/abtests/${exp_id}`, { auth: true }),
  start: (exp_id: string) =>
    api.post<Experiment>(`/abtests/${exp_id}/start`, {}, { auth: true }),
  stop: (exp_id: string, winner?: "a" | "b") =>
    api.post<Experiment>(
      `/abtests/${exp_id}/stop${buildQS({ winner })}`,
      {},
      { auth: true }
    ),
  assign: (exp_id: string, user_id: string) =>
    api.get<{ exp_id: string; user_id: string; arm: "a" | "b" }>(
      `/abtests/${exp_id}/assign${buildQS({ user_id })}`,
      { auth: true }
    ),
};

/* --------------------------- Competitors ------------------------ */

export const competitors = {
  list: () =>
    api.get<{
      ok: boolean;
      competitors: {
        handle: string;
        posts_7d: number;
        avg_engagement: number;
        top_post?: string;
      }[];
    }>("/competitors", { auth: true }),
  posts: (handle: string) =>
    api.get<{
      handle: string;
      posts: { id: string; title: string; engagement: number }[];
    }>(`/competitors/${encodeURIComponent(handle)}/posts`, { auth: true }),
};

/* --------------------------- Sentiment -------------------------- */

export const sentiment = {
  analyze: (text: string) =>
    api.post<{ label: "positive" | "neutral" | "negative"; score: number }>(
      "/sentiment/analyze",
      { text },
      { auth: true }
    ),
};

/* --------------------------- Translate -------------------------- */

export const translate = {
  to: (text: string, target_lang: "en" | "hi" | "es" = "en") =>
    api.post<{ text: string; lang: string }>(
      "/translate",
      { text, target_lang },
      { auth: true }
    ),
};

/* ----------------------------- Growth --------------------------- */

export const growth = {
  checklist: () =>
    api.get<{
      quick_wins: string[];
      playbooks: string[];
      profile_tips: string[];
    }>("/growth/checklist", { auth: true }),
};

/* ----------------------------- Export --------------------------- */

export const exportApi = {
  analyticsCsv: () =>
    api.get<string>("/export/analytics.csv", {
      auth: true,
      headers: { Accept: "text/csv" },
    }),
  analyticsJson: () =>
    api.get<{ ok: boolean; series: Record<string, number[]> }>(
      "/export/analytics.json",
      { auth: true }
    ),
};

/* ---------------------------- LinkedIn -------------------------- */

export const linkedin = {
  schedule: (scheduled_at: string, text: string, media_urls?: string[]) =>
    api.post<{ ok: boolean; scheduled_id: string }>(
      "/linkedin/schedule",
      { scheduled_at, text, media_urls },
      { auth: true }
    ),
  scheduled: () =>
    api.get<{ ok: boolean; items: any[] }>("/linkedin/scheduled", {
      auth: true,
    }),
  publishNow: (text: string, media_urls?: string[]) =>
    api.post<{ ok: boolean; post_id: string; status: "published" }>(
      "/linkedin/publish",
      { text, media_urls },
      { auth: true }
    ),
  metrics: () =>
    api.get<{ ok: boolean; user: string; metrics: Record<string, number> }>(
      "/linkedin/metrics",
      { auth: true }
    ),
};
