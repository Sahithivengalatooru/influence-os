"use client";
import { useState } from "react";
import PostCard from "@/components/PostCard";

type PostType = "text" | "article" | "carousel" | "poll";

export default function PostComposer() {
  const [type, setType] = useState<PostType>("text");
  const [title, setTitle] = useState("How we productionized RAG");
  const [body, setBody] = useState(
    "Three lessons from shipping agentic workflows…"
  );
  const [topic, setTopic] = useState("Agentic RAG for enterprise search");
  const [voice, setVoice] = useState("confident, friendly, concise");
  const [lang, setLang] = useState("en");
  const [n, setN] = useState(2);
  const [variants, setVariants] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  const slidePrompts = [
    "Problem → Approach → Outcome",
    "Framework → Tactics → CTA",
    "Myth → Fact → Tip",
  ];
  const [slides, setSlides] = useState<string[]>(slidePrompts);

  const [pollQ, setPollQ] = useState("How often should we post?");
  const [pollOptions, setPollOptions] = useState([
    "Weekly",
    "Biweekly",
    "Monthly",
  ]);

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

      {type !== "poll" && (
        <>
          <div className="grid gap-1">
            <label className="text-xs">Title</label>
            <input
              className="rounded border p-2"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          <div className="grid gap-1">
            <label className="text-xs">Body / Summary</label>
            <textarea
              className="rounded border p-2"
              rows={4}
              value={body}
              onChange={(e) => setBody(e.target.value)}
            />
          </div>
        </>
      )}

      {type === "carousel" && (
        <div className="grid gap-2">
          <label className="text-xs">Slides (captions)</label>
          {slides.map((s, i) => (
            <input
              key={i}
              className="rounded border p-2"
              value={s}
              onChange={(e) => {
                const next = slides.slice();
                next[i] = e.target.value;
                setSlides(next);
              }}
            />
          ))}
        </div>
      )}

      {type === "poll" && (
        <div className="grid gap-2">
          <label className="text-xs">Poll</label>
          <input
            className="rounded border p-2"
            value={pollQ}
            onChange={(e) => setPollQ(e.target.value)}
          />
          {pollOptions.map((o, i) => (
            <input
              key={i}
              className="rounded border p-2"
              value={o}
              onChange={(e) => {
                const next = pollOptions.slice();
                next[i] = e.target.value;
                setPollOptions(next);
              }}
            />
          ))}
        </div>
      )}

      <div className="grid sm:grid-cols-2 gap-3">
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
      </div>

      <button
        onClick={generate}
        disabled={busy}
        className="w-max rounded bg-black px-3 py-2 text-white"
      >
        {busy ? "Generating..." : "Generate"}
      </button>

      <div className="grid gap-3">
        {variants.map((v, i) => {
          if (type === "text")
            return (
              <PostCard
                key={i}
                type="text"
                title={title || `Variant ${i + 1}`}
                body={v}
              />
            );
          if (type === "article")
            return (
              <PostCard
                key={i}
                type="article"
                title={title || `Variant ${i + 1}`}
                summary={v}
                wordCount={600}
              />
            );
          if (type === "carousel")
            return (
              <PostCard
                key={i}
                type="carousel"
                title={title || `Variant ${i + 1}`}
                slides={[
                  { caption: slides[0] || v.split(".")[0] || "Slide 1" },
                  { caption: slides[1] || v.split(".")[1] || "Slide 2" },
                  { caption: slides[2] || v.split(".")[2] || "Slide 3" },
                ]}
              />
            );
          return (
            <PostCard
              key={i}
              type="poll"
              question={pollQ || v}
              options={pollOptions}
            />
          );
        })}
      </div>
    </div>
  );
}
