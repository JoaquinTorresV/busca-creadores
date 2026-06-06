"""
Cliente de la YouTube Data API v3 (async con httpx).

Adaptado del scraper original: ahora la API key se pasa como parámetro (no es
global) y los errores de la API se traducen a una excepción tipada para que la
ruta los convierta en mensajes claros, sin filtrar detalles internos.
"""

import httpx

BASE = "https://www.googleapis.com/youtube/v3"


class YouTubeAPIError(Exception):
    """Error de la API de YouTube ya traducido a algo presentable al usuario."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _raise_for_api_error(data: dict) -> None:
    """Inspecciona la respuesta de la API y lanza YouTubeAPIError si trae 'error'."""
    if "error" not in data:
        return
    err = data["error"]
    reason = ""
    try:
        reason = err["errors"][0].get("reason", "")
    except (KeyError, IndexError, TypeError):
        reason = ""

    if reason in ("quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded"):
        raise YouTubeAPIError(
            "La cuota diaria de la API de YouTube se agotó. Intenta más tarde "
            "o usa tu propia API key.",
            status_code=429,
        )
    if reason in ("keyInvalid", "badRequest", "forbidden"):
        raise YouTubeAPIError(
            "La API key de YouTube es inválida o no tiene permisos para la "
            "Data API v3.",
            status_code=400,
        )
    raise YouTubeAPIError(
        "Hubo un problema consultando la API de YouTube. Intenta de nuevo.",
        status_code=502,
    )


async def search_channels(
    client: httpx.AsyncClient,
    keyword: str,
    max_results: int,
    language: str,
    api_key: str,
) -> list[str]:
    """Busca channel IDs para UNA keyword. Devuelve lista de IDs únicos."""
    channels: list[str] = []
    page_token = None
    while len(channels) < max_results:
        params = {
            "part": "snippet",
            "q": keyword,
            "type": "channel",
            "maxResults": min(50, max_results - len(channels)),
            "relevanceLanguage": language,
            "key": api_key,
        }
        if page_token:
            params["pageToken"] = page_token

        r = await client.get(f"{BASE}/search", params=params)
        data = r.json()
        _raise_for_api_error(data)

        items = data.get("items", [])
        channels.extend(
            i["id"]["channelId"] for i in items if i.get("id", {}).get("channelId")
        )
        page_token = data.get("nextPageToken")
        if not page_token or not items:
            break

    # Dedup conservando orden, recorte al máximo pedido.
    return list(dict.fromkeys(channels))[:max_results]


async def get_channel_details(
    client: httpx.AsyncClient,
    channel_ids: list[str],
    api_key: str,
) -> list[dict]:
    """Trae snippet + statistics en lotes de 50 IDs."""
    all_data: list[dict] = []
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i : i + 50]
        params = {
            "part": "snippet,statistics",
            "id": ",".join(batch),
            "key": api_key,
        }
        r = await client.get(f"{BASE}/channels", params=params)
        data = r.json()
        _raise_for_api_error(data)
        all_data.extend(data.get("items", []))
    return all_data
