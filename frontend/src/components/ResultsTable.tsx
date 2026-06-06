"use client";

// Tabla de resultados + botón de descarga CSV.

import type { ChannelResult } from "@/lib/types";

interface Props {
  results: ChannelResult[];
  onDownload: () => void;
}

/** Celda con un link a una red social, o "—" si está vacía. */
function LinkCell({ url, label }: { url: string; label: string }) {
  if (!url) return <span className="text-border">—</span>;
  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      className="text-accent hover:underline"
      title={url}
    >
      {label}
    </a>
  );
}

export function ResultsTable({ results, onDownload }: Props) {
  if (results.length === 0) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-medium text-gray-200">
          {results.length} {results.length === 1 ? "creador" : "creadores"}{" "}
          encontrado{results.length === 1 ? "" : "s"}
        </h2>
        <button
          onClick={onDownload}
          className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accentHover"
        >
          ⬇ Descargar CSV
        </button>
      </div>

      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface2 text-xs uppercase tracking-wide text-muted">
            <tr>
              <th className="px-4 py-3">Canal</th>
              <th className="px-4 py-3 text-right">Subs</th>
              <th className="px-4 py-3 text-right">Views</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Redes</th>
              <th className="px-4 py-3">Temática</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {results.map((r, i) => (
              <tr key={i} className="hover:bg-surface2/50">
                <td className="px-4 py-3">
                  <a
                    href={r.canal_url}
                    target="_blank"
                    rel="noreferrer"
                    className="font-medium text-gray-100 hover:text-accent"
                  >
                    {r.nombre}
                  </a>
                </td>
                <td className="px-4 py-3 text-right text-gray-300">{r.subs_fmt}</td>
                <td className="px-4 py-3 text-right text-muted">
                  {r.views.toLocaleString("es")}
                </td>
                <td className="px-4 py-3">
                  {r.email ? (
                    <a
                      href={`mailto:${r.email}`}
                      className="text-accent hover:underline"
                    >
                      {r.email}
                    </a>
                  ) : (
                    <span className="text-border">—</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-x-3 gap-y-1">
                    <LinkCell url={r.instagram} label="IG" />
                    <LinkCell url={r.tiktok} label="TikTok" />
                    <LinkCell url={r.twitter} label="X" />
                    <LinkCell url={r.facebook} label="FB" />
                    <LinkCell url={r.linkedin} label="in" />
                    <LinkCell url={r.website} label="Web" />
                  </div>
                </td>
                <td className="px-4 py-3 text-xs text-muted">{r.keyword_origen}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
