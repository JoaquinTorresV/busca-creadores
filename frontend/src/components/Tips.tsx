// Nota fija con consejos para aprovechar los resultados. Siempre visible.

export function Tips() {
  return (
    <aside className="rounded-xl border border-border bg-surface/40 p-5 text-sm">
      <h3 className="mb-3 flex items-center gap-2 font-medium text-gray-200">
        <span>💡</span> Cómo aprovechar los resultados
      </h3>
      <ul className="space-y-2 text-muted">
        <li className="flex gap-2">
          <span className="text-accent">→</span>
          <span>
            <strong className="text-gray-300">Descarga siempre el CSV.</strong>{" "}
            Ahí queda todo guardado, incluido el{" "}
            <strong className="text-gray-300">link directo a cada canal</strong> de
            YouTube.
          </span>
        </li>
        <li className="flex gap-2">
          <span className="text-accent">→</span>
          <span>
            <strong className="text-gray-300">
              Entra siempre al canal de YouTube
            </strong>{" "}
            usando ese link, aunque el CSV ya traiga redes. A veces el sistema no
            alcanza a capturar todos los links, pero{" "}
            <strong className="text-gray-300">sí están en el canal</strong> (sobre
            todo la web del creador). No te fíes solo de la base de datos: el canal
            siempre tiene la info más actualizada.
          </span>
        </li>
        <li className="flex gap-2">
          <span className="text-accent">→</span>
          <span>
            ¿No ves su Instagram o TikTok? Muchos no los ponen en YouTube, pero sí
            dejan su <strong className="text-gray-300">web personal</strong>. Entra a
            esa web y desde ahí sueles llegar a todas sus redes.
          </span>
        </li>
      </ul>
    </aside>
  );
}
