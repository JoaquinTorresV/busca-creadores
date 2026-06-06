// Genera y descarga un CSV en el cliente (con BOM utf-8-sig para Excel).

import type { ChannelResult } from "./types";

const COLUMNS: { key: keyof ChannelResult; label: string }[] = [
  { key: "nombre", label: "nombre" },
  { key: "suscriptores", label: "suscriptores" },
  { key: "subs_fmt", label: "subs" },
  { key: "views", label: "views" },
  { key: "videos", label: "videos" },
  { key: "email", label: "email" },
  { key: "instagram", label: "instagram" },
  { key: "tiktok", label: "tiktok" },
  { key: "twitter", label: "twitter" },
  { key: "facebook", label: "facebook" },
  { key: "linkedin", label: "linkedin" },
  { key: "website", label: "website" },
  { key: "canal_url", label: "canal_url" },
  { key: "keyword_origen", label: "keyword_origen" },
  { key: "descripcion", label: "descripcion" },
];

/** Escapa un valor según las reglas de CSV (comillas, comas, saltos de línea). */
function escapeCsv(value: string | number): string {
  const s = String(value ?? "");
  if (/[",\n\r]/.test(s)) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

export function downloadCsv(results: ChannelResult[], filename = "creadores_youtube.csv") {
  const header = COLUMNS.map((c) => c.label).join(",");
  const rows = results.map((r) =>
    COLUMNS.map((c) => escapeCsv(r[c.key] as string | number)).join(",")
  );
  const csv = [header, ...rows].join("\r\n");

  // BOM utf-8-sig para que Excel respete los acentos.
  const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
