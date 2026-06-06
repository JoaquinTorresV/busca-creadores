"""
App FastAPI: CORS estricto, router de búsqueda y /health para Render.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes.search import router as search_router

app = FastAPI(
    title="Buscador de Creadores de YouTube — jqsystem",
    description="API que busca creadores de YouTube y extrae sus datos de contacto.",
    version="1.0.0",
)

# ─── CORS estricto: SOLO el dominio del frontend ─────────────
# Nunca usar "*": eso permitiría que cualquier web use nuestra API/cuota.
allowed_origins = [settings.FRONTEND_URL.rstrip("/")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(search_router)


@app.get("/health")
async def health():
    """Endpoint de salud para que Render no mate el servicio."""
    return {"status": "ok"}
