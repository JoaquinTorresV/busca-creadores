// Aviso de posible "cold start" del backend en Render (plan gratis duerme tras 15 min).

export function ColdStartNotice() {
  return (
    <div className="rounded-lg border border-border bg-surface2 px-4 py-3 text-sm text-muted">
      <span className="mr-2">⏳</span>
      La primera búsqueda puede tardar hasta ~1 minuto si el servicio estaba
      inactivo. Las siguientes serán rápidas.
    </div>
  );
}
