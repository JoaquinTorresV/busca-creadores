"use client";

// Campo colapsable para que el usuario pegue SU propia API key de YouTube.
// Se revela cuando se agotan las búsquedas gratis. La key se manda solo en la
// request (nunca se guarda).

import { useState } from "react";

interface Props {
  value: string;
  onChange: (v: string) => void;
  forceOpen?: boolean;
}

export function ApiKeyField({ value, onChange, forceOpen = false }: Props) {
  const [open, setOpen] = useState(forceOpen);

  return (
    <div className="rounded-lg border border-border bg-surface">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium text-gray-200"
      >
        <span>🔑 Usar mi propia API key de YouTube (ilimitado)</span>
        <span className="text-muted">{open ? "−" : "+"}</span>
      </button>

      {open && (
        <div className="space-y-3 border-t border-border px-4 py-4">
          <input
            type="password"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="AIza... (tu API key de YouTube Data API v3)"
            className="w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-gray-100 outline-none focus:border-accent"
            autoComplete="off"
            spellCheck={false}
          />
          <p className="text-xs leading-relaxed text-muted">
            Tu key se usa solo para esta búsqueda y <strong>nunca se guarda</strong>.
            Consíguela gratis:
          </p>
          <ol className="list-decimal space-y-1 pl-5 text-xs leading-relaxed text-muted">
            <li>
              Entra a{" "}
              <a
                href="https://console.cloud.google.com/apis/library/youtube.googleapis.com"
                target="_blank"
                rel="noreferrer"
                className="text-accent hover:underline"
              >
                Google Cloud Console
              </a>{" "}
              y crea un proyecto.
            </li>
            <li>
              Activa <em>YouTube Data API v3</em>.
            </li>
            <li>
              Ve a <em>Credentials → Create credentials → API key</em> y cópiala
              aquí.
            </li>
          </ol>
        </div>
      )}
    </div>
  );
}
