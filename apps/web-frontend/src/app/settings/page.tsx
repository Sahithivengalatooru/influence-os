"use client";
import { useState } from "react";

export default function Settings() {
  const [voice, setVoice] = useState("confident, friendly, concise");
  const [langs, setLangs] = useState("en, hi, es");
  return (
    <div className="grid gap-6 max-w-2xl">
      <h2 className="text-2xl font-semibold">Settings</h2>
      <div className="rounded-xl border p-4 grid gap-3">
        <label className="text-sm font-medium">Brand Voice</label>
        <textarea
          className="w-full rounded border p-2"
          rows={4}
          value={voice}
          onChange={(e) => setVoice(e.target.value)}
        />
      </div>
      <div className="rounded-xl border p-4 grid gap-3">
        <label className="text-sm font-medium">Languages</label>
        <input
          className="rounded border p-2"
          value={langs}
          onChange={(e) => setLangs(e.target.value)}
        />
      </div>
      <div className="text-xs text-gray-500">
        Stored client-side only in the prototype.
      </div>
    </div>
  );
}
