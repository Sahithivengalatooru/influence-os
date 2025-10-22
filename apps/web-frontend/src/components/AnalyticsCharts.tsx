"use client";
import { useEffect, useRef } from "react";

type Series = { label: string; values: number[] };

const defaultEngagement: Series[] = [
  { label: "Likes", values: [10, 18, 14, 22, 30, 26, 33] },
  { label: "Comments", values: [2, 5, 3, 4, 6, 5, 7] },
  { label: "Shares", values: [1, 2, 2, 3, 4, 3, 5] },
];

const defaultRates = {
  ctr: [1.2, 1.5, 1.1, 1.8, 2.1, 2.0, 2.4],
  reach: [300, 420, 380, 520, 600, 570, 680],
};

export default function AnalyticsCharts({
  engagement = defaultEngagement,
  ctr = defaultRates.ctr,
  reach = defaultRates.reach,
}: {
  engagement?: Series[];
  ctr?: number[];
  reach?: number[];
}) {
  const barRef = useRef<HTMLCanvasElement>(null);
  const lineRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const c = barRef.current;
    if (!c) return;
    const ctx = c.getContext("2d")!;
    const w = c.width,
      h = c.height;
    ctx.clearRect(0, 0, w, h);
    const n = engagement[0]?.values.length ?? 0;
    const groups = engagement.length;
    const max = Math.max(1, ...engagement.flatMap((s) => s.values));
    const pad = 24,
      plotW = w - pad * 2,
      plotH = h - pad * 2,
      groupW = plotW / n,
      barW = groupW / (groups + 1);
    engagement.forEach((s, gi) => {
      ctx.beginPath();
      for (let i = 0; i < n; i++) {
        const x = pad + i * groupW + gi * barW;
        const val = s.values[i];
        const bh = (val / max) * plotH;
        const y = h - pad - bh;
        ctx.rect(x, y, barW * 0.9, bh);
      }
      ctx.fillStyle = ["#111", "#666", "#aaa"][gi % 3];
      ctx.fill();
    });
    ctx.fillStyle = "#000";
    ctx.font = "10px sans-serif";
    ctx.fillText("Likes / Comments / Shares", pad, 12);
  }, [engagement]);

  useEffect(() => {
    const c = lineRef.current;
    if (!c) return;
    const ctx = c.getContext("2d")!;
    const w = c.width,
      h = c.height;
    ctx.clearRect(0, 0, w, h);
    const n = Math.max(ctr.length, reach.length);
    const pad = 24,
      plotW = w - pad * 2,
      plotH = h - pad * 2;
    const maxCTR = Math.max(1, ...ctr),
      maxReach = Math.max(1, ...reach);
    const norm = (v: number, m: number) => (v / m) * plotH;
    const draw = (vals: number[], color: string, max: number) => {
      ctx.beginPath();
      vals.forEach((v, i) => {
        const x = pad + (i / (n - 1)) * plotW;
        const y = h - pad - norm(v, max);
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      });
      ctx.strokeStyle = color;
      ctx.stroke();
    };
    draw(ctr, "#111", maxCTR);
    draw(reach, "#888", maxReach);
    ctx.fillStyle = "#000";
    ctx.font = "10px sans-serif";
    ctx.fillText("CTR (%) & Reach (normalized)", pad, 12);
  }, [ctr, reach]);

  return (
    <div className="grid gap-4">
      <canvas ref={barRef} width={520} height={160} className="w-full" />
      <canvas ref={lineRef} width={520} height={160} className="w-full" />
    </div>
  );
}
