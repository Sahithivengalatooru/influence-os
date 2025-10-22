"use client";
import { useState } from "react";

export default function HashtagHelper() {
  const [topic, setTopic] = useState("Agentic RAG for enterprise search");
  const [tags, setTags] = useState<string[]>([]);

  async function run() {
    const res = await fetch("/api/proxy/hashtags/suggest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    });
    const data = await res.json();
    setTags(data.hashtags || []);
  }

  return (
    <div className="rounded-xl border p-4 grid gap-3">
      <div className="text-sm font-medium">Hashtag suggestions</div>
      <input
        className="rounded border p-2"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
      />
      <button onClick={run} className="w-max rounded border px-3 py-1 text-sm">
        Suggest
      </button>
      <div className="flex flex-wrap gap-2">
        {tags.map((t) => (
          <span key={t} className="rounded bg-gray-100 px-2 py-1 text-sm">
            {t}
          </span>
        ))}
      </div>
    </div>
  );
}
