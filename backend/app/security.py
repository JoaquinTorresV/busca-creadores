"""
Helpers de seguridad: obtención de IP del cliente y validación de rangos.

La validación/sanitización del input principal vive en los validadores de
`schemas.py`; aquí van utilidades transversales.
"""

import hashlib
from fastapi import Request

from .config import settings


def get_client_ip(request: Request) -> str:
    """
    Devuelve la IP del cliente.

    En Render (detrás de proxy) la IP real viene en `X-Forwarded-For`.
    Tomamos la primera de la lista. Caemos a request.client si no existe.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def hash_ip(ip: str) -> str:
    """
    Hashea la IP antes de usarla como clave de rate limit.

    Así no guardamos IPs en claro en Redis (privacidad). El día se añade
    aparte en rate_limit.py para que la clave expire por jornada.
    """
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()[:32]


def validate_sub_range(min_subs: int, max_subs: int) -> tuple[int, int]:
    """Normaliza y valida el rango de suscriptores. Lanza ValueError si es inválido."""
    min_subs = max(0, min_subs)
    max_subs = min(max_subs, settings.HARD_MAX_SUBS)
    if min_subs >= max_subs:
        raise ValueError("El mínimo de suscriptores debe ser menor que el máximo.")
    return min_subs, max_subs
