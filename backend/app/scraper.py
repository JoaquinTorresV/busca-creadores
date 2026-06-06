"""
Scraping del /about de cada canal con Playwright (async) + parsers regex.

Reutiliza la lógica del scraper original. Cambios para el backend:
- Async (Playwright async API) para encajar con FastAPI.
- Un único browser/context reutilizado por búsqueda (no uno por canal).
- El fix del beacon de YouTube (i.ytimg.com/generate_204, dominios de Google)
  se conserva en SOCIAL_PATTERNS y en el descarte de "website".
"""

import re
import asyncio
from contextlib import asynccontextmanager

from playwright.async_api import async_playwright

# ─── PARSERS ─────────────────────────────────────────────────
SOCIAL_PATTERNS = {
    "instagram": r"instagram\.com/([^/\s\"'?&]+)",
    "tiktok": r"tiktok\.com/@?([^/\s\"'?&]+)",
    "twitter": r"(?:twitter|x)\.com/([^/\s\"'?&]+)",
    "facebook": r"facebook\.com/([^/\s\"'?&]+)",
    "twitch": r"twitch\.tv/([^/\s\"'?&]+)",
    "linkedin": r"linkedin\.com/(?:in|company)/([^/\s\"'?&]+)",
    "website": (
        r"https?://(?!(?:www\.)?(?:youtube|youtu|ytimg|googlevideo|gstatic|google|"
        r"googleusercontent|schema|instagram|tiktok|twitter|x|facebook|twitch|"
        r"linkedin|linktr)\.)[^\s\"'<>&]+"
    ),
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


def parse_email(text: str) -> str:
    match = EMAIL_RE.search(text or "")
    return match.group(0).strip() if match else ""


def parse_socials(text: str) -> dict:
    socials: dict = {}
    for platform, pattern in SOCIAL_PATTERNS.items():
        match = re.search(pattern, text or "", re.IGNORECASE)
        if not match:
            continue
        if platform == "website":
            url = match.group(0).rstrip("/.,;)")
        else:
            handle = match.group(1).rstrip("/.,;)")
            url = f"https://{platform}.com/{handle}"
        socials[platform] = url
    return socials


def format_number(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


# ─── BLOQUEO DE RECURSOS PESADOS ─────────────────────────────
_BLOCK_RE = re.compile(
    r"\.(png|jpg|jpeg|gif|svg|woff|woff2|mp4|webp)(\?|$)", re.IGNORECASE
)


async def _block_heavy(route):
    if _BLOCK_RE.search(route.request.url):
        await route.abort()
    else:
        await route.continue_()


# ─── BROWSER REUTILIZABLE ────────────────────────────────────
@asynccontextmanager
async def browser_page():
    """
    Context manager que abre Playwright + Chromium + un page reutilizable.
    Se usa una vez por búsqueda; el mismo page sirve para todos los canales.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="es-ES",
        )
        page = await context.new_page()
        await page.route("**/*", _block_heavy)
        try:
            yield page
        finally:
            await browser.close()


async def scrape_about(page, channel_id: str) -> tuple[str, dict]:
    """Extrae (email, socials) del /about de un canal. Nunca lanza: devuelve vacío si falla."""
    url = f"https://www.youtube.com/channel/{channel_id}/about"
    email = ""
    socials: dict = {}
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        try:
            await page.wait_for_selector(
                "#channel-container, ytd-channel-about-metadata-renderer, "
                "yt-page-header-renderer",
                timeout=8000,
            )
        except Exception:
            pass

        full_text = await page.inner_text("body")
        full_html = await page.content()

        email = parse_email(full_text) or parse_email(full_html)

        socials = {**parse_socials(full_text), **parse_socials(full_html)}

        links = await page.eval_on_selector_all(
            "a[href]", "els => els.map(el => el.href)"
        )
        for link in links:
            for k, v in parse_socials(link).items():
                socials.setdefault(k, v)

        # Descarta falsos positivos de "website": YouTube y su beacon de tracking.
        web = socials.get("website", "")
        if web and ("youtube.com" in web or "generate_204" in web):
            del socials["website"]
    except Exception:
        # No loggeamos detalles para no exponer datos; devolvemos lo que haya.
        pass
    return email, socials
