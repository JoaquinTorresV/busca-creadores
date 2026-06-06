// Contador de búsquedas gratis restantes.

export function SearchCounter({ remaining }: { remaining: number | null }) {
  if (remaining === null) {
    // Usó su propia API key: búsquedas ilimitadas.
    return (
      <span className="text-sm text-muted">
        Usando tu propia API key — búsquedas ilimitadas
      </span>
    );
  }

  const isLow = remaining <= 1;
  return (
    <span className={`text-sm ${isLow ? "text-amber-400" : "text-muted"}`}>
      {remaining > 0
        ? `Te ${remaining === 1 ? "queda" : "quedan"} ${remaining} ${
            remaining === 1 ? "búsqueda gratis" : "búsquedas gratis"
          }`
        : "Agotaste tus búsquedas gratis de hoy"}
    </span>
  );
}
