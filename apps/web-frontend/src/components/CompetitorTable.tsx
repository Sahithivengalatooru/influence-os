"use client";
import { useEffect, useState } from "react";

type Row = {
  handle: string;
  posts_7d: number;
  avg_engagement: number;
  top_post?: string;
};

export default function CompetitorTable() {
  const [rows, setRows] = useState<Row[]>([]);
  const [busy, setBusy] = useState(false);

  async function load() {
    setBusy(true);
    try {
      const res = await fetch("/api/proxy/competitors");
      const data = await res.json();
      setRows(data.competitors || []);
    } finally {
      setBusy(false);
    }
  }
  useEffect(() => {
    load();
  }, []);

  return (
    <div className="rounded-xl border overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="p-2 text-left">Handle</th>
            <th className="p-2 text-left">Posts (7d)</th>
            <th className="p-2 text-left">Avg Engagement</th>
            <th className="p-2 text-left">Top Post</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-t">
              <td className="p-2">{r.handle}</td>
              <td className="p-2">{r.posts_7d}</td>
              <td className="p-2">{r.avg_engagement}%</td>
              <td className="p-2">{r.top_post}</td>
            </tr>
          ))}
          {!rows.length && (
            <tr>
              <td colSpan={4} className="p-3 text-gray-500">
                {busy ? "Loading…" : "No data"}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
