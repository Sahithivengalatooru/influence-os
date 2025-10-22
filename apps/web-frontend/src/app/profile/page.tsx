"use client";

import { useState } from "react";

type AnalyzeRes = {
  strengths: string[];
  themes: string[];
  suggestions: string[];
};

export default function ProfilePage() {
  const [headline, setHeadline] = useState(
    "PM @ Startup — shipping AI features that users love"
  );
  const [about, setAbout] = useState(
    "I build AI/ML products, shipped RAG & agentic workflows..."
  );
  const [res, setRes] = useState<AnalyzeRes | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function analyze() {
    setBusy(true);
    setError(null);
    setRes(null);
    try {
      const r = await fetch("/api/proxy/profile/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify({ headline, about }),
      });
      if (!r.ok) {
        let msg = `${r.status} ${r.statusText}`;
        try {
          const j = await r.json();
          msg = j?.detail || j?.error || msg;
        } catch {}
        throw new Error(msg);
      }
      const data = (await r.json()) as AnalyzeRes;
      setRes(data);
    } catch (e: any) {
      setError(e?.message || "Failed to analyze");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-6">
      <h2 className="text-2xl font-semibold">Profile Analysis</h2>

      <div className="rounded-xl border p-4 grid gap-3">
        <div className="grid gap-1">
          <label className="text-xs">Headline</label>
          <input
            className="rounded border p-2"
            value={headline}
            onChange={(e) => setHeadline(e.target.value)}
          />
        </div>

        <div className="grid gap-1">
          <label className="text-xs">About</label>
          <textarea
            className="rounded border p-2 h-32"
            value={about}
            onChange={(e) => setAbout(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={analyze}
            disabled={busy}
            className="rounded bg-black px-3 py-2 text-white"
          >
            {busy ? "Analyzing..." : "Analyze"}
          </button>
          {error && (
            <span className="text-sm rounded bg-red-100 text-red-700 px-2 py-1">
              {error}
            </span>
          )}
        </div>
      </div>

      <div className="rounded-xl border p-4 grid gap-3">
        <h3 className="font-medium">Results</h3>

        <div>
          <div className="text-sm font-semibold">Strengths:</div>
          <ul className="list-disc ml-6">
            {res?.strengths?.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>

        <div>
          <div className="text-sm font-semibold">Themes:</div>
          <div className="flex flex-wrap gap-2">
            {res?.themes?.map((t, i) => (
              <span key={i} className="rounded bg-gray-100 px-2 py-1 text-sm">
                {t}
              </span>
            ))}
          </div>
        </div>

        <div>
          <div className="text-sm font-semibold">Suggestions:</div>
          <ul className="list-disc ml-6">
            {res?.suggestions?.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
