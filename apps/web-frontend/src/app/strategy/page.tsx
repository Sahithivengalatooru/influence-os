"use client";
import { useState } from "react";

export default function StrategyPage() {
  const [plan, setPlan] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  async function generate() {
    setBusy(true);
    try {
      const res = await fetch("/api/proxy/strategy/plan", { method: "POST" });
      setPlan(await res.json());
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-6">
      <h2 className="text-2xl font-semibold">Content Strategy</h2>
      <button
        onClick={generate}
        disabled={busy}
        className="w-max rounded bg-black px-3 py-2 text-white"
      >
        {busy ? "Generating..." : "Generate Plan"}
      </button>
      {plan && (
        <div className="grid gap-4">
          <section className="rounded-xl border p-4">
            <h3 className="font-medium mb-2">Objectives</h3>
            <ul className="list-disc ml-5">
              {plan.objectives?.map((o: string, i: number) => (
                <li key={i}>{o}</li>
              ))}
            </ul>
          </section>
          <section className="rounded-xl border p-4">
            <h3 className="font-medium mb-2">Pillars</h3>
            <ul className="list-disc ml-5">
              {plan.pillars?.map((p: any, i: number) => (
                <li key={i}>
                  <b>{p.name}:</b> {p.description}
                </li>
              ))}
            </ul>
          </section>
          <section className="rounded-xl border p-4">
            <h3 className="font-medium mb-2">Cadence</h3>
            <div className="text-sm">Posts/week: {plan.cadence?.per_week}</div>
            <div className="flex flex-wrap gap-2 mt-2">
              {plan.cadence?.windows?.map((w: string, i: number) => (
                <span key={i} className="rounded bg-gray-100 px-2 py-1 text-sm">
                  {w}
                </span>
              ))}
            </div>
          </section>
          <section className="rounded-xl border p-4">
            <h3 className="font-medium mb-2">KPIs</h3>
            <div className="flex flex-wrap gap-2">
              {plan.kpis?.map((k: string, i: number) => (
                <span key={i} className="rounded bg-gray-100 px-2 py-1 text-sm">
                  {k}
                </span>
              ))}
            </div>
          </section>
          <section className="rounded-xl border p-4">
            <h3 className="font-medium mb-2">Next Steps</h3>
            <ul className="list-disc ml-5">
              {plan.next_steps?.map((s: string, i: number) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </section>
        </div>
      )}
    </div>
  );
}
