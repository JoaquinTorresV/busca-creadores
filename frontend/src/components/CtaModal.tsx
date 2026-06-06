"use client";

// Modal que aparece al descargar el CSV. Valor agregado, no venta agresiva.

interface Props {
  open: boolean;
  onClose: () => void;
}

export function CtaModal({ open, onClose }: Props) {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-md rounded-2xl border border-border bg-surface p-7 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-muted transition-colors hover:text-gray-200"
          aria-label="Cerrar"
        >
          ✕
        </button>

        <div className="mb-4 text-3xl">🚀</div>
        <h3 className="mb-3 text-lg font-semibold text-gray-100">
          Listo, tu CSV se está descargando
        </h3>
        <p className="mb-5 text-sm leading-relaxed text-gray-300">
          Espero que esta herramienta te sirva para encontrar a los creadores
          ideales. Si quieres un socio que te ayude a{" "}
          <span className="text-gray-100">
            crear el sistema para montarle una comunidad
          </span>{" "}
          a tu creador — escríbeme. Y suerte con cerrar tu cliente. 🤝
        </p>

        <a
          href="https://instagram.com/joaquin_torres_v"
          target="_blank"
          rel="noreferrer"
          className="flex items-center justify-center gap-2 rounded-lg bg-accent px-4 py-3 text-sm font-medium text-white transition-colors hover:bg-accentHover"
        >
          📸 Instagram: @joaquin_torres_v
        </a>

        <button
          onClick={onClose}
          className="mt-3 w-full text-center text-xs text-muted hover:text-gray-300"
        >
          Seguir buscando
        </button>
      </div>
    </div>
  );
}
