"use client";

import { useEffect, useRef, useState } from "react";

type TrendsResponse = { topics: string[] };

export default function TrendsPage() {
  const [industry, setIndustry] = useState("AI/ML");
  const [seed, setSeed] = useState("RAG");
  const [count, setCount] = useState(10); // how many topics to show (3..25)
  const [topics, setTopics] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  async function load() {
    // cancel any in-flight request to avoid races
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setBusy(true);
    setError(null);

    try {
      const qs = new URLSearchParams({
        industry,
        seed,
        n: String(Math.min(25, Math.max(3, count))),
        shuffle: "true",
        // salt forces variety and also busts any caches along the path
        salt: Date.now().toString(),
      }).toString();

      const res = await fetch(`/api/proxy/trends?${qs}`, {
        cache: "no-store",
        signal: controller.signal,
      });

      if (!res.ok) {
        // proxy returns JSON on errors; still guard parsing
        let detail = `${res.status} ${res.statusText}`;
        try {
          const j = (await res.json()) as any;
          if (j?.detail)
            detail =
              typeof j.detail === "string"
                ? j.detail
                : JSON.stringify(j.detail);
          if (j?.error) detail = `${j.error}: ${j.detail ?? detail}`;
        } catch {
          /* ignore */
        }
        throw new Error(detail);
      }

      const data = (await res.json()) as TrendsResponse;
      setTopics(Array.isArray(data.topics) ? data.topics : []);
    } catch (e: any) {
      if (e?.name !== "AbortError") {
        setError(e?.message || "Failed to load trends");
        setTopics([]);
      }
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="grid gap-6">
      <h2 className="text-2xl font-semibold">Industry Trends</h2>

      <div className="rounded-xl border p-4 flex flex-wrap gap-3 items-end">
        <div className="grid gap-1">
          <label className="text-xs">Industry</label>
          <input
            className="rounded border p-2"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
            placeholder="e.g., AI/ML"
          />
        </div>

        <div className="grid gap-1">
          <label className="text-xs">Seed</label>
          <input
            className="rounded border p-2"
            value={seed}
            onChange={(e) => setSeed(e.target.value)}
            placeholder="e.g., RAG"
          />
        </div>

        <div className="grid gap-1">
          <label className="text-xs">Count</label>
          <input
            type="number"
            min={3}
            max={25}
            className="rounded border p-2 w-24"
            value={count}
            onChange={(e) => setCount(Number(e.target.value || 10))}
          />
        </div>

        <button
          onClick={load}
          disabled={busy}
          className="rounded bg-black px-3 py-2 text-white"
        >
          {busy ? "Loading..." : "Refresh"}
        </button>

        {error && (
          <div className="ml-auto text-sm rounded bg-red-100 text-red-700 px-3 py-2">
            {error}
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-2">
        {topics.map((t, i) => (
          <span
            key={`${t}-${i}`}
            className="rounded bg-gray-100 px-2 py-1 text-sm"
            title={t}
          >
            {t}
          </span>
        ))}
        {!busy && topics.length === 0 && !error && (
          <div className="text-sm text-gray-500">
            No topics yet. Try Refresh.
          </div>
        )}
      </div>
    </div>
  );
}
