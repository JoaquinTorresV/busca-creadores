"""
YouTube Channel Scraper v2 - jqsystem
Busca creadores con HISTORIAS DE TRANSFORMACIÓN (no nichos genéricos)
Extrae: email, redes sociales, suscriptores, views, descripción
Usa Playwright para renderizado real del /about page

NOVEDADES v2:
- Búsqueda con MÚLTIPLES keywords en una corrida (KEYWORDS = lista)
- Keywords enfocadas en narrativa personal / transformación
- API key leída desde variable de entorno (no hardcodeada)
- Dedup global entre keywords + columna "keyword_origen"
- Rango por defecto 500–10k subs
"""

import re
import os
import csv
import time
from playwright.sync_api import sync_playwright
import requests

# Carga las variables del archivo .env (si python-dotenv está instalado)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─── CONFIGURACIÓN ───────────────────────────────────────────
# La API key se lee del archivo .env (en la misma carpeta que este script).
# El .env debe tener una línea así:
#   YT_API_KEY=tu_key_aqui
API_KEY = os.environ.get("YT_API_KEY", "")

# Varias búsquedas en una sola corrida.
# Estas capturan la narrativa de "cambio / pasé de 0 a X" en vez de nichos genéricos.
KEYWORDS = [
    # Transformación general / marca personal
    "como pase de 0 a",
    "mi historia de cambio",
    "como cambie mi vida",
    "deje mi trabajo para",
    "marca personal desde cero",

    # Mindset / disciplina
    "disciplina cambio mi vida",
    "mentalidad transformacion",

    # Fitness con historia
    "mi transformacion fisica",
    "como baje de peso historia",

    # Negocios / dinero con narrativa personal (no "curso")
    "como empece mi negocio desde cero",
    "de quiebra a",
]

MIN_SUBS    = 500
MAX_SUBS    = 10_000
MAX_PER_KW  = 50          # resultados por keyword
LANGUAGE    = "es"
OUTPUT_FILE = "canales_youtube_v2.csv"

# ─── PARSERS ─────────────────────────────────────────────────
SOCIAL_PATTERNS = {
    "instagram": r"instagram\.com/([^/\s\"'?&]+)",
    "tiktok":    r"tiktok\.com/@?([^/\s\"'?&]+)",
    "twitter":   r"(?:twitter|x)\.com/([^/\s\"'?&]+)",
    "facebook":  r"facebook\.com/([^/\s\"'?&]+)",
    "twitch":    r"twitch\.tv/([^/\s\"'?&]+)",
    "linkedin":  r"linkedin\.com/(?:in|company)/([^/\s\"'?&]+)",
    "website":   r"https?://(?!(?:www\.)?(?:youtube|instagram|tiktok|twitter|x|facebook|twitch|linkedin|linktr|youtu|ytimg|gstatic|googlevideo|google|googleusercontent|schema)\.)[^\s\"'<>&]+",
}

def parse_email(text):
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0).strip() if match else ""

def parse_socials(text):
    socials = {}
    for platform, pattern in SOCIAL_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if platform == "website":
                url = match.group(0).rstrip("/.,;)")
            else:
                handle = match.group(1).rstrip("/.,;)")
                url = f"https://{platform}.com/{handle}"
            socials[platform] = url
    return socials

def format_number(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)

# ─── YOUTUBE API ─────────────────────────────────────────────
BASE = "https://www.googleapis.com/youtube/v3"

def search_channels(keyword, max_results, language):
    """Busca channel IDs para UNA keyword. Devuelve lista de (channel_id, keyword)."""
    channels = []
    page_token = None
    while len(channels) < max_results:
        params = {
            "part": "snippet",
            "q": keyword,
            "type": "channel",
            "maxResults": min(50, max_results - len(channels)),
            "relevanceLanguage": language,
            "key": API_KEY,
        }
        if page_token:
            params["pageToken"] = page_token
        r = requests.get(f"{BASE}/search", params=params)
        data = r.json()
        if "error" in data:
            print(f"  [ERROR API] {data['error']['message']}")
            break
        items = data.get("items", [])
        channels.extend([i["id"]["channelId"] for i in items])
        page_token = data.get("nextPageToken")
        if not page_token or not items:
            break
    return list(dict.fromkeys(channels))[:max_results]

def get_channel_details(channel_ids):
    all_data = []
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i+50]
        params = {
            "part": "snippet,statistics",
            "id": ",".join(batch),
            "key": API_KEY,
        }
        r = requests.get(f"{BASE}/channels", params=params)
        data = r.json()
        all_data.extend(data.get("items", []))
    return all_data

# ─── PLAYWRIGHT SCRAPER ───────────────────────────────────────
def scrape_about_playwright(page, channel_id):
    url = f"https://www.youtube.com/channel/{channel_id}/about"
    email   = ""
    socials = {}
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        try:
            page.wait_for_selector(
                "#channel-container, ytd-channel-about-metadata-renderer, yt-page-header-renderer",
                timeout=8000,
            )
        except:
            pass

        full_text = page.inner_text("body")
        full_html = page.content()

        email = parse_email(full_text) or parse_email(full_html)

        socials_text = parse_socials(full_text)
        socials_html = parse_socials(full_html)
        socials = {**socials_text, **socials_html}

        links = page.eval_on_selector_all("a[href]", "els => els.map(el => el.href)")
        for link in links:
            for k, v in parse_socials(link).items():
                if k not in socials:
                    socials[k] = v

        if "website" in socials and (
            "youtube.com" in socials["website"]
            or "generate_204" in socials["website"]
        ):
            del socials["website"]
    except Exception as e:
        print(f"    [WARN] Playwright error: {e}")
    return email, socials

# ─── PIPELINE PRINCIPAL ───────────────────────────────────────
def run():
    if not API_KEY:
        print("[!] Falta la API key. Crea un archivo .env en esta carpeta con:")
        print("    YT_API_KEY=tu_key_aqui")
        print("    Y asegurate de tener instalado python-dotenv (pip install python-dotenv)")
        return

    print(f"\n{'='*55}")
    print(f"  YouTube Channel Scraper v2 — jqsystem")
    print(f"  Keywords: {len(KEYWORDS)} búsquedas de transformación")
    print(f"  Subs    : {format_number(MIN_SUBS)} – {format_number(MAX_SUBS)}")
    print(f"{'='*55}\n")

    # 1) Buscar IDs para todas las keywords, guardando de qué keyword vino cada uno
    print("[1/3] Buscando canales por keyword...")
    id_to_keyword = {}
    for kw in KEYWORDS:
        ids = search_channels(kw, MAX_PER_KW, LANGUAGE)
        nuevos = 0
        for cid in ids:
            if cid not in id_to_keyword:
                id_to_keyword[cid] = kw
                nuevos += 1
        print(f'      "{kw}" → {len(ids)} encontrados ({nuevos} nuevos)')
        time.sleep(0.3)

    all_ids = list(id_to_keyword.keys())
    print(f"      → {len(all_ids)} canales únicos en total\n")

    # 2) Stats + filtro por rango de subs
    print("[2/3] Obteniendo stats y filtrando por rango...")
    raw_channels = get_channel_details(all_ids)
    filtered = []
    for ch in raw_channels:
        subs = int(ch.get("statistics", {}).get("subscriberCount", 0))
        if subs < MIN_SUBS or subs > MAX_SUBS:
            continue
        filtered.append(ch)
    print(f"      → {len(filtered)} canales en rango {format_number(MIN_SUBS)}–{format_number(MAX_SUBS)}\n")

    if not filtered:
        print("[!] Sin canales en ese rango. Ajusta MIN_SUBS / MAX_SUBS.")
        return

    # 3) Scrape /about
    print("[3/3] Scrapeando /about con Playwright...\n")
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            locale="es-ES",
        )
        page = context.new_page()
        page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,mp4,webp}", lambda r: r.abort())

        for i, ch in enumerate(filtered, 1):
            snippet = ch.get("snippet", {})
            stats   = ch.get("statistics", {})
            channel_id  = ch["id"]
            name        = snippet.get("title", "")
            subs        = int(stats.get("subscriberCount", 0))
            views       = int(stats.get("viewCount", 0))
            videos      = int(stats.get("videoCount", 0))
            description = snippet.get("description", "")
            channel_url = f"https://youtube.com/channel/{channel_id}"

            print(f"  [{i}/{len(filtered)}] {name} ({format_number(subs)} subs)...")

            email_api   = parse_email(description)
            socials_api = parse_socials(description)
            email_pw, socials_pw = scrape_about_playwright(page, channel_id)
            email   = email_pw or email_api
            socials = {**socials_api, **socials_pw}

            if email:
                print(f"    ✅ Email: {email}")
            for k, v in socials.items():
                print(f"    🔗 {k}: {v}")

            results.append({
                "nombre":         name,
                "suscriptores":   subs,
                "subs_fmt":       format_number(subs),
                "views":          views,
                "videos":         videos,
                "email":          email,
                "instagram":      socials.get("instagram", ""),
                "tiktok":         socials.get("tiktok", ""),
                "twitter":        socials.get("twitter", ""),
                "facebook":       socials.get("facebook", ""),
                "website":        socials.get("website", ""),
                "canal_url":      channel_url,
                "keyword_origen": id_to_keyword.get(channel_id, ""),
                "descripcion":    description[:200],
            })
            time.sleep(1.5)

        browser.close()

    results.sort(key=lambda x: x["suscriptores"], reverse=True)

    fieldnames = list(results[0].keys())
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    with_email = sum(1 for r in results if r["email"])
    with_ig    = sum(1 for r in results if r["instagram"])
    with_tt    = sum(1 for r in results if r["tiktok"])

    print(f"\n{'='*55}")
    print(f"  ✅ Completado — {len(results)} canales exportados")
    print(f"  📧 Con email:     {with_email}/{len(results)}")
    print(f"  📸 Con Instagram: {with_ig}/{len(results)}")
    print(f"  🎵 Con TikTok:    {with_tt}/{len(results)}")
    print(f"  💾 Archivo:       {OUTPUT_FILE}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    run()