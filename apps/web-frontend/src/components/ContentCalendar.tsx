"use client";
import { useMemo, useState } from "react";

type Slot = {
  id: string;
  date: string;
  title: string;
  status?: "draft" | "scheduled" | "published";
};

const iso = (d: Date) => d.toISOString().slice(0, 10);

export default function ContentCalendar() {
  const [slots, setSlots] = useState<Slot[]>([
    {
      id: "p1",
      date: iso(new Date()),
      title: "Thought leadership post",
      status: "draft",
    },
    {
      id: "p2",
      date: iso(new Date()),
      title: "Carousel: AI trends",
      status: "draft",
    },
  ]);

  const days = useMemo(() => {
    const out: string[] = [];
    const start = new Date();
    start.setDate(start.getDate() - start.getDay()); // previous Sunday
    for (let i = 0; i < 14; i++) {
      const d = new Date(start);
      d.setDate(start.getDate() + i);
      out.push(iso(d));
    }
    return out;
  }, []);

  const onDragStart = (e: React.DragEvent<HTMLLIElement>, id: string) => {
    e.dataTransfer.setData("text/plain", id);
    e.dataTransfer.effectAllowed = "move";
  };

  const onDrop = (e: React.DragEvent<HTMLDivElement>, date: string) => {
    e.preventDefault();
    const id = e.dataTransfer.getData("text/plain");
    setSlots((prev) => prev.map((s) => (s.id === id ? { ...s, date } : s)));
  };

  const onDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  };

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {days.map((d) => {
        const daySlots = slots.filter((s) => s.date === d);
        return (
          <div
            key={d}
            className="rounded-lg border p-2 min-h-28"
            onDrop={(e) => onDrop(e, d)}
            onDragOver={onDragOver}
          >
            <div className="mb-2 text-xs text-gray-500">{d}</div>
            <ul className="space-y-1">
              {daySlots.map((s) => (
                <li
                  key={s.id}
                  draggable
                  onDragStart={(e) => onDragStart(e, s.id)}
                  className="cursor-grab rounded bg-gray-100 px-2 py-1 text-xs active:cursor-grabbing"
                  title="Drag to reschedule"
                >
                  {s.title}{" "}
                  {s.status ? (
                    <span className="text-[10px] text-gray-500">
                      ({s.status})
                    </span>
                  ) : null}
                </li>
              ))}
            </ul>
            <button
              className="mt-2 w-full rounded border px-2 py-1 text-xs"
              onClick={() =>
                setSlots((prev) => [
                  ...prev,
                  {
                    id:
                      globalThis.crypto?.randomUUID?.() ??
                      Math.random().toString(36).slice(2),
                    date: d,
                    title: "New draft",
                    status: "draft",
                  },
                ])
              }
            >
              + Add
            </button>
          </div>
        );
      })}
    </div>
  );
}
