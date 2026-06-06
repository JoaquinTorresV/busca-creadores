"""
Endpoint POST /search — orquesta YouTube API + Playwright + rate limit.

Flujo:
1. Valida/sanitiza input (en SearchRequest).
2. Decide qué key usar: la del usuario (si vino) o la del dueño.
3. Si usa la del dueño → aplica rate limit por IP.
4. Busca canales por keyword (con dedup global + keyword_origen).
5. Trae stats, filtra por rango de subs, recorta al cap.
6. Scrapea /about de cada canal con un browser reutilizado.
7. Devuelve JSON con resultados + búsquedas restantes.

Nunca se loggea la API key ni los emails extraídos.
"""

import asyncio

import httpx
from fastapi import APIRouter, Request, HTTPException

from ..config import settings
from ..schemas import SearchRequest, SearchResponse, ChannelResult
from ..security import get_client_ip, validate_sub_range
from ..youtube import search_channels, get_channel_details, YouTubeAPIError
from ..scraper import browser_page, scrape_about, parse_email, parse_socials, format_number
from ..rate_limit import check_and_consume, peek_remaining

router = APIRouter()

# GET de cortesía para que el front muestre las búsquedas restantes al cargar.


@router.get("/quota")
async def quota(request: Request):
    """Cuántas búsquedas gratis le quedan a esta IP hoy (sin consumir)."""
    ip = get_client_ip(request)
    remaining = await peek_remaining(ip)
    return {"remaining": remaining, "limit": settings.FREE_LIMIT_PER_DAY}


@router.post("/search", response_model=SearchResponse)
async def search(request: Request, body: SearchRequest):
    # ─── Validar rango de subs ────────────────────────────────
    try:
        min_subs, max_subs = validate_sub_range(body.min_subs, body.max_subs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # ─── Elegir API key ───────────────────────────────────────
    using_own_key = not body.user_api_key
    api_key = body.user_api_key or settings.YT_API_KEY

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="El servicio no tiene una API key configurada. Intenta con tu propia key.",
        )

    ip = get_client_ip(request)
    remaining: int | None = None

    async with httpx.AsyncClient(timeout=30) as client:
        # ─── Rate limit (solo si usa la key del dueño) ────────
        if using_own_key:
            allowed, remaining = await check_and_consume(ip)
            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail=(
                        "Llegaste al límite de búsquedas gratis por hoy. "
                        "Pega tu propia API key de YouTube para seguir buscando."
                    ),
                )

        # ─── 1) Buscar IDs por keyword (dedup global) ─────────
        id_to_keyword: dict[str, str] = {}
        try:
            for kw in body.keywords:
                ids = await search_channels(
                    client, kw, settings.MAX_PER_KW, body.language, api_key
                )
                for cid in ids:
                    id_to_keyword.setdefault(cid, kw)
        except YouTubeAPIError as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)

        all_ids = list(id_to_keyword.keys())
        if not all_ids:
            return SearchResponse(
                results=[], total=0, remaining=remaining, used_own_key=using_own_key
            )

        # ─── 2) Stats + filtro por rango ──────────────────────
        try:
            raw = await get_channel_details(client, all_ids, api_key)
        except YouTubeAPIError as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)

    filtered = []
    for ch in raw:
        subs = int(ch.get("statistics", {}).get("subscriberCount", 0))
        if min_subs <= subs <= max_subs:
            filtered.append(ch)

    # Mayor a menor y recorte al cap para no exceder el timeout.
    filtered.sort(
        key=lambda c: int(c.get("statistics", {}).get("subscriberCount", 0)),
        reverse=True,
    )
    filtered = filtered[: settings.MAX_CHANNELS_PER_SEARCH]

    if not filtered:
        return SearchResponse(
            results=[], total=0, remaining=remaining, used_own_key=using_own_key
        )

    # ─── 3) Scrape /about con browser reutilizado ─────────────
    results: list[ChannelResult] = []
    async with browser_page() as page:
        for ch in filtered:
            snippet = ch.get("snippet", {})
            stats = ch.get("statistics", {})
            channel_id = ch["id"]
            description = snippet.get("description", "")

            # De la descripción (API) + del /about (Playwright). Playwright manda.
            email_api = parse_email(description)
            socials_api = parse_socials(description)
            email_pw, socials_pw = await scrape_about(page, channel_id)

            email = email_pw or email_api
            socials = {**socials_api, **socials_pw}
            subs = int(stats.get("subscriberCount", 0))

            results.append(
                ChannelResult(
                    nombre=snippet.get("title", ""),
                    suscriptores=subs,
                    subs_fmt=format_number(subs),
                    views=int(stats.get("viewCount", 0)),
                    videos=int(stats.get("videoCount", 0)),
                    email=email,
                    instagram=socials.get("instagram", ""),
                    tiktok=socials.get("tiktok", ""),
                    twitter=socials.get("twitter", ""),
                    facebook=socials.get("facebook", ""),
                    linkedin=socials.get("linkedin", ""),
                    website=socials.get("website", ""),
                    canal_url=f"https://youtube.com/channel/{channel_id}",
                    keyword_origen=id_to_keyword.get(channel_id, ""),
                    descripcion=description[:200],
                )
            )
            await asyncio.sleep(settings.SCRAPE_DELAY)

    return SearchResponse(
        results=results,
        total=len(results),
        remaining=remaining,
        used_own_key=using_own_key,
    )
