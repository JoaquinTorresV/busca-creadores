"""
Rate limit por IP/día usando Redis estándar (redis-py async).

Funciona con cualquier Redis: Redis Cloud, Upstash (endpoint redis://), local, etc.
Solo necesita la variable de entorno REDIS_URL.

Clave: ratelimit:{hash_ip}:{YYYY-MM-DD}. Hacemos INCR y, en el primer uso del
día, ponemos EXPIRE ~26h para que la clave se limpie sola.

Se OMITE por completo cuando el usuario trae su propia API key (esa búsqueda no
consume cuota del dueño, así que no se limita).

Si REDIS_URL no está configurada, el límite degrada a "permitir" (fail-open) y se
avisa en logs sin detener el servicio — útil en desarrollo local.
"""

from datetime import date

import redis.asyncio as redis

from .config import settings
from .security import hash_ip

_TTL_SECONDS = 26 * 60 * 60  # un poco más de un día

# Cliente Redis perezoso (se crea una sola vez y se reutiliza).
_client: redis.Redis | None = None


def _get_client() -> redis.Redis | None:
    global _client
    if not settings.REDIS_URL:
        return None
    if _client is None:
        _client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
    return _client


def _key_for(ip: str) -> str:
    today = date.today().isoformat()
    return f"ratelimit:{hash_ip(ip)}:{today}"


async def check_and_consume(ip: str) -> tuple[bool, int]:
    """
    Registra un uso para esta IP hoy.

    Devuelve (permitido, restantes). Si Redis no está configurado o falla,
    hace fail-open (permite) sin exponer el error.
    """
    limit = settings.FREE_LIMIT_PER_DAY
    client = _get_client()

    if client is None:
        print("[rate_limit] REDIS_URL no configurada — límite desactivado (solo dev).")
        return True, limit

    key = _key_for(ip)
    try:
        count = int(await client.incr(key))
        if count == 1:
            # Primer uso del día: fija expiración.
            await client.expire(key, _TTL_SECONDS)
    except Exception:
        print("[rate_limit] Error consultando Redis — se permite la request.")
        return True, limit

    remaining = max(0, limit - count)
    allowed = count <= limit
    return allowed, remaining


async def peek_remaining(ip: str) -> int:
    """Consulta cuántas búsquedas gratis quedan sin consumir una."""
    limit = settings.FREE_LIMIT_PER_DAY
    client = _get_client()
    if client is None:
        return limit
    try:
        val = await client.get(_key_for(ip))
        count = int(val) if val is not None else 0
    except Exception:
        return limit
    return max(0, limit - count)
