"use client";

// Indicador de progreso para la búsqueda. Como el backend hace una sola request
// síncrona (sin eventos de progreso reales), mostramos una barra indeterminada +
// mensajes que van avanzando + un contador de segundos, para que se note que está
// trabajando y no colgado.

import { useEffect, useState } from "react";

// Cada mensaje aparece a partir del segundo indicado. Se queda en el último.
const STEPS = [
  { at: 0, label: "Conectando con YouTube…" },
  { at: 3, label: "Buscando canales por temática…" },
  { at: 8, label: "Filtrando por suscriptores…" },
  { at: 13, label: "Abriendo perfiles y extrayendo redes y emails…" },
  { at: 35, label: "Casi listo, ordenando resultados…" },
];

export function SearchProgress() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, []);

  // Último mensaje cuyo "at" ya pasó.
  const message =
    [...STEPS].reverse().find((s) => seconds >= s.at)?.label ?? STEPS[0].label;

  return (
    <div className="mt-8 rounded-xl border border-border bg-surface/60 p-5">
      <div className="mb-3 flex items-center justify-between text-sm">
        <span className="text-gray-200">{message}</span>
        <span className="tabular-nums text-muted">{seconds}s</span>
      </div>

      {/* Barra indeterminada */}
      <div className="relative h-1.5 w-full overflow-hidden rounded-full bg-surface2">
        <span className="animate-indeterminate bg-accent" />
      </div>

      <p className="mt-3 text-xs text-muted">
        Analizamos cada canal abriendo su perfil real, así que puede tardar hasta
        ~1&nbsp;min. No cierres esta pestaña.
      </p>
    </div>
  );
}
