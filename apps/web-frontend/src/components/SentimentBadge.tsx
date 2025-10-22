"use client";
import { useEffect, useState } from "react";

export default function SentimentBadge({ text }: { text: string }) {
  const [label, setLabel] = useState<"positive" | "neutral" | "negative">(
    "neutral"
  );
  const [score, setScore] = useState(0.5);

  useEffect(() => {
    const id = setTimeout(async () => {
      const res = await fetch("/api/proxy/sentiment/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      setLabel(data.label || "neutral");
      setScore(data.score || 0.5);
    }, 300);
    return () => clearTimeout(id);
  }, [text]);

  const color =
    label === "positive"
      ? "bg-green-100 text-green-700 border-green-200"
      : label === "negative"
      ? "bg-red-100 text-red-700 border-red-200"
      : "bg-gray-100 text-gray-700 border-gray-200";

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-2 py-1 text-xs ${color}`}
    >
      <span className="font-medium capitalize">{label}</span>
      <span className="opacity-70">{Math.round(score * 100)}%</span>
    </span>
  );
}
