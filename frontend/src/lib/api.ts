// Cliente HTTP hacia el backend de Render.

import type { SearchParams, SearchResponse } from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

/** Mensaje de error legible a partir de una respuesta fallida. */
async function readError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail) && data.detail[0]?.msg) return data.detail[0].msg;
  } catch {
    /* ignore */
  }
  if (res.status === 429) return "Llegaste al límite de búsquedas por hoy.";
  return "Ocurrió un error al buscar. Intenta de nuevo.";
}

export async function searchChannels(params: SearchParams): Promise<SearchResponse> {
  const res = await fetch(`${API_URL}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

/** Consulta cuántas búsquedas gratis quedan (sin consumir). */
export async function getQuota(): Promise<{ remaining: number; limit: number }> {
  const res = await fetch(`${API_URL}/quota`, { cache: "no-store" });
  if (!res.ok) throw new Error("No se pudo consultar la cuota.");
  return res.json();
}
