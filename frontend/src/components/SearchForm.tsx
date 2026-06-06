"use client";

// Formulario de búsqueda: 1–3 keywords dinámicas + filtros (rango de subs, idioma).

import { useState } from "react";

const MAX_KEYWORDS = 3;

export interface SearchFormValues {
  keywords: string[];
  minSubs: number;
  maxSubs: number;
  language: string;
}

interface Props {
  onSearch: (values: SearchFormValues) => void;
  loading: boolean;
  disabled: boolean;
}

export function SearchForm({ onSearch, loading, disabled }: Props) {
  const [keywords, setKeywords] = useState<string[]>([""]);
  const [minSubs, setMinSubs] = useState(500);
  const [maxSubs, setMaxSubs] = useState(10000);
  const [language, setLanguage] = useState("es");

  const updateKeyword = (i: number, v: string) => {
    setKeywords((kw) => kw.map((k, idx) => (idx === i ? v : k)));
  };

  const addKeyword = () => {
    if (keywords.length < MAX_KEYWORDS) setKeywords((kw) => [...kw, ""]);
  };

  const removeKeyword = (i: number) => {
    setKeywords((kw) => kw.filter((_, idx) => idx !== i));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleaned = keywords.map((k) => k.trim()).filter(Boolean);
    if (cleaned.length === 0) return;
    onSearch({ keywords: cleaned, minSubs, maxSubs, language });
  };

  const canSearch = keywords.some((k) => k.trim()) && !loading && !disabled;

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Keywords */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-200">
          Temáticas a buscar{" "}
          <span className="text-muted">(hasta {MAX_KEYWORDS})</span>
        </label>
        {keywords.map((kw, i) => (
          <div key={i} className="flex gap-2">
            <input
              type="text"
              value={kw}
              onChange={(e) => updateKeyword(i, e.target.value)}
              placeholder='Ej: "marca personal desde cero"'
              maxLength={120}
              className="flex-1 rounded-lg border border-border bg-surface px-4 py-3 text-sm text-gray-100 outline-none focus:border-accent"
            />
            {keywords.length > 1 && (
              <button
                type="button"
                onClick={() => removeKeyword(i)}
                className="rounded-lg border border-border px-3 text-muted transition-colors hover:text-gray-200"
                aria-label="Quitar keyword"
              >
                ✕
              </button>
            )}
          </div>
        ))}
        {keywords.length < MAX_KEYWORDS && (
          <button
            type="button"
            onClick={addKeyword}
            className="text-sm text-accent hover:underline"
          >
            + Agregar otra temática
          </button>
        )}
      </div>

      {/* Filtros */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-muted">
            Suscriptores mín.
          </label>
          <input
            type="number"
            min={0}
            value={minSubs}
            onChange={(e) => setMinSubs(Number(e.target.value))}
            className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-gray-100 outline-none focus:border-accent"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-muted">
            Suscriptores máx.
          </label>
          <input
            type="number"
            min={1}
            value={maxSubs}
            onChange={(e) => setMaxSubs(Number(e.target.value))}
            className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-gray-100 outline-none focus:border-accent"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-muted">Idioma</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-gray-100 outline-none focus:border-accent"
          >
            <option value="es">Español</option>
            <option value="en">Inglés</option>
            <option value="pt">Portugués</option>
            <option value="fr">Francés</option>
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={!canSearch}
        className="w-full rounded-lg bg-accent px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-accentHover disabled:cursor-not-allowed disabled:opacity-40"
      >
        {loading ? "Buscando creadores…" : "Buscar creadores"}
      </button>
    </form>
  );
}
