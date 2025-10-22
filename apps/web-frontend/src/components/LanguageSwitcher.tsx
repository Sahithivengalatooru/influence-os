"use client";
import { useState } from "react";

export default function LanguageSwitcher() {
  const [lang, setLang] = useState("en");
  return (
    <div className="flex items-center gap-2">
      <label className="text-sm">Language</label>
      <select
        className="rounded border p-1 text-sm"
        value={lang}
        onChange={(e) => setLang(e.target.value)}
      >
        <option value="en">English</option>
        <option value="hi">Hindi</option>
        <option value="es">Spanish</option>
      </select>
    </div>
  );
}
