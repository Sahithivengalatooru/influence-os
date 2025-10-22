"use client";
import { useEffect, useState } from "react";

export default function GrowthPage() {
  const [data, setData] = useState<any>(null);
  async function load() {
    const res = await fetch("/api/proxy/growth/checklist");
    setData(await res.json());
  }
  useEffect(() => {
    load();
  }, []);

  return (
    <div className="grid gap-6">
      <h2 className="text-2xl font-semibold">Growth Checklist</h2>
      {data ? (
        <div className="grid gap-4">
          <section className="rounded-xl border p-4">
            <h3 className="font-medium mb-2">Quick Wins</h3>
            <ul className="list-disc ml-5">
              {data.quick_wins?.map((s: string, i: number) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </section>
          <section className="rounded-xl border p-4">
            <h3 className="font-medium mb-2">Playbooks</h3>
            <ul className="list-disc ml-5">
              {data.playbooks?.map((s: string, i: number) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </section>
          <section className="rounded-xl border p-4">
            <h3 className="font-medium mb-2">Profile Tips</h3>
            <ul className="list-disc ml-5">
              {data.profile_tips?.map((s: string, i: number) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </section>
        </div>
      ) : (
        <div className="text-sm text-gray-600">Loading…</div>
      )}
    </div>
  );
}
