"use client";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";

const ContentCalendar = dynamic(() => import("@/components/ContentCalendar"), {
  ssr: false,
});

type Item = { id: string; date: string; title: string; status: string };

export default function CalendarPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [date, setDate] = useState<string>(
    new Date().toISOString().slice(0, 10)
  );
  const [title, setTitle] = useState("New draft");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    const res = await fetch("/api/proxy/calendar");
    setItems(await res.json());
  }
  useEffect(() => {
    refresh();
  }, []);

  async function add() {
    setBusy(true);
    try {
      await fetch("/api/proxy/calendar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date, title }),
      });
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-8">
      <h2 className="text-2xl font-semibold">Calendar</h2>
      <section className="rounded-xl border p-4">
        <h3 className="font-medium mb-2">Visual Planner</h3>
        <ContentCalendar />
      </section>
      <section className="grid gap-4">
        <div className="rounded-xl border p-4 flex flex-wrap items-end gap-3">
          <div className="grid gap-1">
            <label className="text-xs">Date</label>
            <input
              type="date"
              className="rounded border p-2"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
          <div className="grid gap-1">
            <label className="text-xs">Title</label>
            <input
              className="rounded border p-2"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          <button
            onClick={add}
            disabled={busy}
            className="rounded bg-black px-3 py-2 text-white"
          >
            {busy ? "Adding..." : "Add item"}
          </button>
        </div>
        <div className="rounded-xl border p-4">
          <h3 className="font-medium mb-2">Items</h3>
          <ul className="text-sm space-y-1">
            {items.map((i) => (
              <li key={i.id} className="flex justify-between border-b py-1">
                <span>
                  {i.date} — {i.title}{" "}
                  <span className="text-gray-500">({i.status})</span>
                </span>
                <form
                  action={`/api/proxy/calendar/${i.id}`}
                  method="POST"
                  className="hidden"
                />
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}
