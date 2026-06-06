"""
Configuración central del backend.

Todas las claves y URLs sensibles se leen de variables de entorno (nunca
hardcodeadas). En local se pueden poner en un archivo `.env` (ver `.env.example`);
en Render se configuran como Environment Variables del servicio.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ─── Secretos (env) ───────────────────────────────────────
    # API key de YouTube del DUEÑO. Vive solo aquí, en el backend.
    YT_API_KEY: str = ""

    # Dominio del frontend autorizado para CORS (ej: https://miapp.vercel.app).
    # En local: http://localhost:3000
    FRONTEND_URL: str = "http://localhost:3000"

    # Redis para el rate limit persistente. Acepta cualquier Redis estándar
    # (Redis Cloud, Upstash, local…). Formato de la URL de conexión:
    #   redis://default:CONTRASEÑA@host:puerto        (sin TLS)
    #   rediss://default:CONTRASEÑA@host:puerto       (con TLS)
    REDIS_URL: str = ""

    # ─── Caps / límites (no secretos) ─────────────────────────
    MAX_KEYWORDS: int = 3              # keywords por búsqueda
    MAX_PER_KW: int = 15              # channel IDs a pedir por keyword
    MAX_CHANNELS_PER_SEARCH: int = 25  # tope de canales a scrapear por búsqueda
    FREE_LIMIT_PER_DAY: int = 3        # búsquedas gratis por IP/día con la key del dueño
    SCRAPE_DELAY: float = 0.5          # pausa (s) entre canales en Playwright

    # Rango de suscriptores por defecto / topes de validación
    DEFAULT_MIN_SUBS: int = 500
    DEFAULT_MAX_SUBS: int = 10_000
    HARD_MAX_SUBS: int = 100_000_000   # tope absoluto para validar input

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
