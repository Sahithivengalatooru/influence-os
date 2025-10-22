"use client";

import { useState } from "react";

type Experiment = {
  id: string;
  name: string;
  goal: string;
  a: string;
  b: string;
  status: "created" | "running" | "stopped";
  metrics?: {
    views: { A: number; B: number };
    clicks: { A: number; B: number };
  };
};

async function jsonOrThrow(res: Response) {
  const text = await res.text();
  let data: any = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    /* ignore */
  }
  if (!res.ok) {
    const msg =
      data?.detail || data?.error || `${res.status} ${res.statusText}`;
    throw new Error(msg);
  }
  return data;
}

export default function ABTestWizard() {
  const [name, setName] = useState("headline-variants");
  const [goal, setGoal] = useState("CTR");
  const [a, setA] = useState("How we cut RAG latency by 40%");
  const [b, setB] = useState("We shipped a faster RAG—here's how");
  const [exp, setExp] = useState<Experiment | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [userId, setUserId] = useState("demo-user");
  const [assigned, setAssigned] = useState<"A" | "B" | null>(null);

  async function create() {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/proxy/abtests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify({ name, goal, a, b }),
      });
      const data = (await jsonOrThrow(res)) as Experiment;
      setExp(data);
      setAssigned(null);
    } catch (e: any) {
      setError(e.message || "Create failed");
    } finally {
      setBusy(false);
    }
  }

  async function start() {
    if (!exp?.id) return;
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`/api/proxy/abtests/${exp.id}/start`, {
        method: "POST",
        cache: "no-store",
      });
      const data = (await jsonOrThrow(res)) as Experiment;
      setExp(data);
    } catch (e: any) {
      setError(e.message || "Start failed");
    } finally {
      setBusy(false);
    }
  }

  async function stop() {
    if (!exp?.id) return;
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`/api/proxy/abtests/${exp.id}/stop`, {
        method: "POST",
        cache: "no-store",
      });
      const data = (await jsonOrThrow(res)) as Experiment;
      setExp(data);
    } catch (e: any) {
      setError(e.message || "Stop failed");
    } finally {
      setBusy(false);
    }
  }

  async function assign() {
    if (!exp?.id) return;
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(
        `/api/proxy/abtests/${exp.id}/assign?user_id=${encodeURIComponent(
          userId || "anon"
        )}`,
        { cache: "no-store" }
      );
      const data = await jsonOrThrow(res);
      setAssigned(data.variant as "A" | "B");
      // also refresh experiment to reflect view counters
      const r2 = await fetch(`/api/proxy/abtests/${exp.id}`, {
        cache: "no-store",
      });
      setExp((await jsonOrThrow(r2)) as Experiment);
    } catch (e: any) {
      setError(e.message || "Assign failed");
    } finally {
      setBusy(false);
    }
  }

  async function click(variant: "A" | "B") {
    if (!exp?.id) return;
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(
        `/api/proxy/abtests/${exp.id}/click?variant=${variant}`,
        { method: "POST", cache: "no-store" }
      );
      await jsonOrThrow(res);
      // refresh experiment to show updated click counters
      const r2 = await fetch(`/api/proxy/abtests/${exp.id}`, {
        cache: "no-store",
      });
      setExp((await jsonOrThrow(r2)) as Experiment);
    } catch (e: any) {
      setError(e.message || "Click failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-6">
      <div className="rounded-xl border p-4 grid gap-3">
        <div className="grid sm:grid-cols-2 gap-3">
          <input
            className="rounded border p-2"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Experiment name"
          />
          <input
            className="rounded border p-2"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="Goal (e.g., CTR, CVR)"
          />
        </div>

        <input
          className="rounded border p-2"
          value={a}
          onChange={(e) => setA(e.target.value)}
          placeholder="Variant A"
        />
        <input
          className="rounded border p-2"
          value={b}
          onChange={(e) => setB(e.target.value)}
          placeholder="Variant B"
        />

        <div className="flex gap-2 flex-wrap">
          <button
            onClick={create}
            disabled={busy}
            className="rounded bg-black px-3 py-2 text-white"
          >
            Create
          </button>
          <button
            onClick={start}
            disabled={busy || !exp}
            className="rounded border px-3 py-2"
          >
            Start
          </button>
          <button
            onClick={stop}
            disabled={busy || !exp}
            className="rounded border px-3 py-2"
          >
            Stop
          </button>

          {error && (
            <span className="ml-auto text-sm rounded bg-red-100 text-red-700 px-2 py-1">
              {error}
            </span>
          )}
        </div>
      </div>

      <div className="rounded-xl border p-4 grid gap-3 text-sm">
        <div>
          <b>ID:</b> {exp?.id ?? ""}
        </div>
        <div>
          <b>Status:</b> {exp?.status ?? ""}
        </div>
        <div>
          <b>A:</b> {exp?.a ?? ""}
        </div>
        <div>
          <b>B:</b> {exp?.b ?? ""}
        </div>

        {exp && (
          <>
            <div className="flex items-end gap-3 flex-wrap">
              <div className="grid gap-1">
                <label className="text-xs">Assign user_id</label>
                <input
                  className="rounded border p-2"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  placeholder="user id for deterministic assignment"
                />
              </div>
              <button
                onClick={assign}
                disabled={busy || exp.status !== "running"}
                className="rounded border px-3 py-2"
              >
                Assign
              </button>
              {assigned && (
                <span className="text-xs rounded bg-gray-100 px-2 py-1">
                  Assigned: {assigned}
                </span>
              )}
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => click("A")}
                disabled={busy || exp.status !== "running"}
                className="rounded border px-3 py-2"
              >
                Click A
              </button>
              <button
                onClick={() => click("B")}
                disabled={busy || exp.status !== "running"}
                className="rounded border px-3 py-2"
              >
                Click B
              </button>
            </div>

            {exp.metrics && (
              <div className="text-xs text-gray-700">
                <div>
                  <b>Views</b> — A: {exp.metrics.views.A} · B:{" "}
                  {exp.metrics.views.B}
                </div>
                <div>
                  <b>Clicks</b> — A: {exp.metrics.clicks.A} · B:{" "}
                  {exp.metrics.clicks.B}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
