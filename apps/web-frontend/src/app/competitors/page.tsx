"use client";
import { useEffect, useState } from "react";

export default function CompetitorsPage() {
  const [list, setList] = useState<any[]>([]);

  async function load() {
    const res = await fetch("/api/proxy/competitors");
    const data = await res.json();
    setList(data.competitors || []);
  }
  useEffect(() => {
    load();
  }, []);

  return (
    <div className="grid gap-6">
      <h2 className="text-2xl font-semibold">Competitor Insights</h2>
      <div className="grid gap-3">
        {list.map((c, i) => (
          <div key={i} className="rounded-xl border p-4">
            <div className="font-medium">{c.handle}</div>
            <div className="text-sm text-gray-600">
              Posts (7d): {c.posts_7d}
            </div>
            <div className="text-sm text-gray-600">
              Avg Engagement: {c.avg_engagement}%
            </div>
            <div className="text-sm text-gray-600">Top Post: {c.top_post}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
