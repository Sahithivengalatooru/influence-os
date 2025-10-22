"use client";
import { useEffect, useState } from "react";

export default function TrendTicker() {
  const [items, setItems] = useState<string[]>([
    "AI safety",
    "RAG",
    "Qwen 2.5",
    "Agentic workflows",
  ]);
  useEffect(() => {
    const id = setInterval(() => setItems((x) => [...x.slice(1), x[0]]), 2500);
    return () => clearInterval(id);
  }, []);
  return (
    <div className="flex gap-2 overflow-hidden text-sm">
      {items.map((t, i) => (
        <span key={i} className="rounded bg-gray-100 px-2 py-1">
          {t}
        </span>
      ))}
    </div>
  );
}
