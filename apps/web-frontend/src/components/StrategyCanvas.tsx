"use client";
import { useEffect, useState } from "react";

type Plan = {
  objectives: string[];
  pillars: { name: string; description: string }[];
  cadence: { per_week: number; windows: string[] };
  kpis: string[];
  next_steps: string[];
};

export default function StrategyCanvas() {
  const [plan, setPlan] = useState<Plan | null>(null);
  const [busy, setBusy] = useState(false);

  async function load() {
    setBusy(true);
    try {
      const res = await fetch("/api/proxy/strategy/plan", { method: "POST" });
      setPlan(await res.json());
    } finally {
      setBusy(false);
    }
  }
  useEffect(() => {
    load();
  }, []);

  if (!plan)
    return (
      <div className="text-sm text-gray-500">
        {busy ? "Loading…" : "No plan yet."}
      </div>
    );

  return (
    <div className="grid gap-4">
      <section className="rounded-xl border p-4">
        <h3 className="font-medium mb-2">Objectives</h3>
        <ul className="list-disc ml-5">
          {plan.objectives.map((o, i) => (
            <li key={i}>{o}</li>
          ))}
        </ul>
      </section>
      <section className="rounded-xl border p-4">
        <h3 className="font-medium mb-2">Pillars</h3>
        <ul className="list-disc ml-5">
          {plan.pillars.map((p, i) => (
            <li key={i}>
              <b>{p.name}:</b> {p.description}
            </li>
          ))}
        </ul>
      </section>
      <section className="rounded-xl border p-4">
        <h3 className="font-medium mb-2">Cadence</h3>
        <div className="text-sm">Posts/week: {plan.cadence.per_week}</div>
        <div className="flex flex-wrap gap-2 mt-2">
          {plan.cadence.windows.map((w, i) => (
            <span key={i} className="rounded bg-gray-100 px-2 py-1 text-sm">
              {w}
            </span>
          ))}
        </div>
      </section>
      <section className="rounded-xl border p-4">
        <h3 className="font-medium mb-2">KPIs</h3>
        <div className="flex flex-wrap gap-2">
          {plan.kpis.map((k, i) => (
            <span key={i} className="rounded bg-gray-100 px-2 py-1 text-sm">
              {k}
            </span>
          ))}
        </div>
      </section>
      <section className="rounded-xl border p-4">
        <h3 className="font-medium mb-2">Next Steps</h3>
        <ul className="list-disc ml-5">
          {plan.next_steps.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}
