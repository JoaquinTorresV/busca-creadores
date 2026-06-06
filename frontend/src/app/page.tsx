"use client";

import { useEffect, useState } from "react";
import { SearchForm, type SearchFormValues } from "@/components/SearchForm";
import { ResultsTable } from "@/components/ResultsTable";
import { SearchCounter } from "@/components/SearchCounter";
import { SearchProgress } from "@/components/SearchProgress";
import { Tips } from "@/components/Tips";
import { ApiKeyField } from "@/components/ApiKeyField";
import { ColdStartNotice } from "@/components/ColdStartNotice";
import { CtaModal } from "@/components/CtaModal";
import { searchChannels, getQuota } from "@/lib/api";
import { downloadCsv } from "@/lib/csv";
import type { ChannelResult } from "@/lib/types";

export default function Home() {
  const [results, setResults] = useState<ChannelResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [showCta, setShowCta] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // Al cargar, consulta las búsquedas restantes.
  useEffect(() => {
    getQuota()
      .then((q) => setRemaining(q.remaining))
      .catch(() => setRemaining(null));
  }, []);

  // El campo de API key se revela al agotar las búsquedas gratis.
  const freeExhausted = remaining !== null && remaining <= 0;

  const handleSearch = async (values: SearchFormValues) => {
    setLoading(true);
    setError(null);
    setHasSearched(true);
    try {
      const res = await searchChannels({
        keywords: values.keywords,
        min_subs: values.minSubs,
        max_subs: values.maxSubs,
        language: values.language,
        user_api_key: apiKey.trim() || undefined,
      });
      setResults(res.results);
      setRemaining(res.remaining);
      if (res.results.length === 0) {
        setError("No se encontraron creadores en ese rango. Prueba ampliar el rango de suscriptores u otra temática.");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error desconocido.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    downloadCsv(results);
    setShowCta(true);
  };

  return (
    <main className="mx-auto max-w-4xl px-5 py-12">
      {/* Header */}
      <header className="mb-10 text-center">
        <h1 className="mb-2 text-3xl font-bold tracking-tight text-gray-50 sm:text-4xl">
          Buscador de Creadores de YouTube
        </h1>
        <p className="text-sm text-muted">
          Encuentra creadores por temática y exporta sus datos de contacto a CSV.
        </p>
      </header>

      {/* Tarjeta de búsqueda */}
      <section className="rounded-2xl border border-border bg-surface/60 p-6 shadow-xl sm:p-8">
        <div className="mb-5 flex items-center justify-between">
          <span className="text-xs uppercase tracking-wide text-muted">
            Nueva búsqueda
          </span>
          <SearchCounter remaining={remaining} />
        </div>

        <SearchForm
          onSearch={handleSearch}
          loading={loading}
          disabled={freeExhausted && !apiKey.trim()}
        />

        {/* Campo de API key propia (se abre solo al agotar las gratis) */}
        {(freeExhausted || apiKey) && (
          <div className="mt-5">
            <ApiKeyField value={apiKey} onChange={setApiKey} forceOpen={freeExhausted} />
          </div>
        )}
      </section>

      {/* Aviso de cold start (antes de la primera búsqueda) */}
      {!hasSearched && (
        <div className="mt-5">
          <ColdStartNotice />
        </div>
      )}

      {/* Consejos fijos: descargar CSV + revisar la web por las redes */}
      <div className="mt-5">
        <Tips />
      </div>

      {/* Estado de carga: barra de progreso + mensajes rotativos */}
      {loading && <SearchProgress />}

      {/* Error */}
      {error && !loading && (
        <div className="mt-6 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-300">
          {error}
        </div>
      )}

      {/* Resultados */}
      {!loading && results.length > 0 && (
        <section className="mt-8">
          <ResultsTable results={results} onDownload={handleDownload} />
        </section>
      )}

      <footer className="mt-16 text-center text-xs text-muted">
        Hecho por{" "}
        <a
          href="https://instagram.com/joaquin_torres_v"
          target="_blank"
          rel="noreferrer"
          className="text-accent hover:underline"
        >
          @joaquin_torres_v
        </a>
      </footer>

      <CtaModal open={showCta} onClose={() => setShowCta(false)} />
    </main>
  );
}
