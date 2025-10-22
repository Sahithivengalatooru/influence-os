"use client";
import { useState } from "react";
import PostCard from "@/components/PostCard";

type PostType = "text" | "article" | "carousel" | "poll";

export default function ComposePage() {
  const [type, setType] = useState<PostType>("text");
  const [topic, setTopic] = useState("Agentic RAG for enterprise search");
  const [voice, setVoice] = useState("confident, friendly, concise");
  const [lang, setLang] = useState("en");
  const [n, setN] = useState(2);
  const [variants, setVariants] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  async function generate() {
    setBusy(true);
    try {
      const res = await fetch("/api/proxy/content/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type,
          topic,
          brand_voice: voice,
          language: lang,
          n_variants: n,
        }),
      });
      const data = await res.json();
      setVariants(data.variants || []);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-6">
      <h2 className="text-2xl font-semibold">Post Composer</h2>
      <div className="rounded-xl border p-4 grid gap-3">
        <div className="grid sm:grid-cols-2 gap-3">
          <div className="grid gap-1">
            <label className="text-xs">Type</label>
            <select
              className="rounded border p-2"
              value={type}
              onChange={(e) => setType(e.target.value as PostType)}
            >
              <option value="text">Text</option>
              <option value="article">Article</option>
              <option value="carousel">Carousel</option>
              <option value="poll">Poll</option>
            </select>
          </div>
          <div className="grid gap-1">
            <label className="text-xs">Language</label>
            <input
              className="rounded border p-2"
              value={lang}
              onChange={(e) => setLang(e.target.value)}
            />
          </div>
        </div>
        <div className="grid gap-1">
          <label className="text-xs">Topic</label>
          <input
            className="rounded border p-2"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
        </div>
        <div className="grid gap-1">
          <label className="text-xs">Brand Voice</label>
          <input
            className="rounded border p-2"
            value={voice}
            onChange={(e) => setVoice(e.target.value)}
          />
        </div>
        <div className="grid gap-1 w-40">
          <label className="text-xs">Variants</label>
          <input
            type="number"
            min={1}
            max={5}
            className="rounded border p-2"
            value={n}
            onChange={(e) => setN(parseInt(e.target.value || "1"))}
          />
        </div>
        <button
          onClick={generate}
          disabled={busy}
          className="w-max rounded bg-black px-3 py-2 text-white"
        >
          {busy ? "Generating..." : "Generate"}
        </button>
      </div>

      <div className="grid gap-3">
        {variants.map((v, i) => {
          if (type === "text")
            return (
              <PostCard
                key={i}
                type="text"
                title={`Variant ${i + 1}`}
                body={v}
              />
            );
          if (type === "article")
            return (
              <PostCard
                key={i}
                type="article"
                title={`Variant ${i + 1}`}
                summary={v}
                wordCount={600}
              />
            );
          if (type === "carousel")
            return (
              <PostCard
                key={i}
                type="carousel"
                title={`Variant ${i + 1}`}
                slides={[
                  { caption: v.split(".")[0] || "Slide 1" },
                  { caption: v.split(".")[1] || "Slide 2" },
                  { caption: v.split(".")[2] || "Slide 3" },
                ]}
              />
            );
          return (
            <PostCard
              key={i}
              type="poll"
              question={v}
              options={["Option A", "Option B", "Option C"]}
            />
          );
        })}
      </div>
    </div>
  );
}
