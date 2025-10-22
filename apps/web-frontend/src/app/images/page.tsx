"use client";

import { useState } from "react";

type ImageRes = { width: number; height: number; data_url: string };

export default function ImagesPage() {
  const [title, setTitle] = useState("AI + community building tips");
  const [bullets, setBullets] = useState(
    "Host office hours; Rituals > random; Spotlight members"
  );
  const [template, setTemplate] = useState<
    "poster" | "split" | "quote" | "stat"
  >("poster");
  const [brand, setBrand] = useState("indigo");
  const [ratio, setRatio] = useState<"square" | "portrait" | "landscape">(
    "square"
  );
  const [img, setImg] = useState<ImageRes | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setBusy(true);
    setError(null);
    try {
      const payload = {
        title,
        bullets: bullets.split(/[,;]\s*/).filter(Boolean),
        template,
        brand,
        ratio,
        width: 1080,
      };
      const r = await fetch("/api/proxy/images/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify(payload),
      });
      if (!r.ok) throw new Error((await r.text()) || r.statusText);
      setImg(await r.json());
    } catch (e: any) {
      setError(e.message || "Failed to generate");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-4">
      <h2 className="text-2xl font-semibold">Image Generation (prototype)</h2>

      <div className="rounded-xl border p-4 grid gap-3">
        <input
          className="rounded border p-2"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Title"
        />
        <input
          className="rounded border p-2"
          value={bullets}
          onChange={(e) => setBullets(e.target.value)}
          placeholder="Bullets (comma or semicolon separated)"
        />

        <div className="flex flex-wrap gap-3">
          <select
            className="rounded border p-2"
            value={template}
            onChange={(e) => setTemplate(e.target.value as any)}
          >
            <option value="poster">Poster</option>
            <option value="split">Split</option>
            <option value="quote">Quote</option>
            <option value="stat">Stat</option>
          </select>
          <select
            className="rounded border p-2"
            value={brand}
            onChange={(e) => setBrand(e.target.value)}
          >
            <option>slate</option>
            <option>indigo</option>
            <option>emerald</option>
            <option>rose</option>
            <option>amber</option>
          </select>
          <select
            className="rounded border p-2"
            value={ratio}
            onChange={(e) => setRatio(e.target.value as any)}
          >
            <option>square</option>
            <option>portrait</option>
            <option>landscape</option>
          </select>
          <button
            onClick={generate}
            disabled={busy}
            className="rounded bg-black px-3 py-2 text-white"
          >
            {busy ? "Generating..." : "Generate"}
          </button>
          {error && (
            <span className="text-sm rounded bg-red-100 text-red-700 px-2 py-1">
              {error}
            </span>
          )}
        </div>
      </div>

      {img && (
        <div className="rounded-xl border p-2">
          <img
            src={img.data_url}
            alt={title}
            className="w-full h-auto rounded-xl"
          />
          <div className="text-xs text-gray-500 p-2">
            Generated {img.width}×{img.height}
          </div>
          <a
            download="poster.png"
            href={img.data_url}
            className="text-sm underline"
          >
            Download PNG
          </a>
        </div>
      )}
    </div>
  );
}
