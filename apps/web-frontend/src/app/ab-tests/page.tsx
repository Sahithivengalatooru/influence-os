"use client";
import { useState } from "react";

export default function ABTestsPage() {
  const [name, setName] = useState("headline-variants");
  const [goal, setGoal] = useState("CTR");
  const [a, setA] = useState("How we cut RAG latency by 40%");
  const [b, setB] = useState("We shipped a faster RAG—here’s how");
  const [exp, setExp] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  async function create() {
    setBusy(true);
    try {
      const res = await fetch("/api/proxy/abtests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, goal, a, b }),
      });
      setExp(await res.json());
    } finally {
      setBusy(false);
    }
  }

  async function start() {
    if (!exp?.id) return;
    const res = await fetch(`/api/proxy/abtests/${exp.id}/start`, {
      method: "POST",
    });
    setExp(await res.json());
  }

  async function stop() {
    if (!exp?.id) return;
    const res = await fetch(`/api/proxy/abtests/${exp.id}/stop`, {
      method: "POST",
    });
    setExp(await res.json());
  }

  return (
    <div className="grid gap-6 max-w-3xl">
      <h2 className="text-2xl font-semibold">A/B Experiments</h2>
      <div className="rounded-xl border p-4 grid gap-3">
        <div className="grid sm:grid-cols-2 gap-3">
          <input
            className="rounded border p-2"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name"
          />
          <input
            className="rounded border p-2"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="Goal"
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
        <div className="flex gap-2">
          <button
            onClick={create}
            disabled={busy}
            className="rounded bg-black px-3 py-2 text-white"
          >
            Create
          </button>
          <button
            onClick={start}
            disabled={!exp}
            className="rounded border px-3 py-2"
          >
            Start
          </button>
          <button
            onClick={stop}
            disabled={!exp}
            className="rounded border px-3 py-2"
          >
            Stop
          </button>
        </div>
      </div>
      {exp && (
        <div className="rounded-xl border p-4 text-sm">
          <div>ID: {exp.id}</div>
          <div>Status: {exp.status}</div>
          <div>A: {exp.a}</div>
          <div>B: {exp.b}</div>
          {exp.winner && <div>Winner: {exp.winner}</div>}
        </div>
      )}
    </div>
  );
}
