# Buscador de Creadores de YouTube — jqsystem

App web para buscar creadores de YouTube por temática, filtrarlos por
suscriptores y exportar sus datos de contacto (email + redes) a CSV.

```
Usuario → Frontend (Next.js / Vercel) → Backend (FastAPI / Render) → YouTube Data API v3 + Playwright
```

- **Frontend** (`frontend/`): Next.js 16 + TypeScript + Tailwind. Interfaz de
  búsqueda, tabla de resultados, descarga CSV y CTA.
- **Backend** (`backend/`): FastAPI. Expone el scraper como API REST, corre
  Playwright (Chromium) para extraer redes del `/about` de cada canal.

## Seguridad (cómo está resuelta)

- La API key del dueño vive **solo** en el backend (env var `YT_API_KEY`); nunca
  viaja al frontend ni al cliente.
- `.env` está en `.gitignore`. Los `.env.example` **no** llevan valores reales.
- **CORS estricto**: el backend solo acepta el dominio definido en `FRONTEND_URL`.
- **Rate limit** de 3 búsquedas/IP/día con la key del dueño, persistido en Upstash
  Redis. El usuario puede pegar **su propia API key** para búsquedas ilimitadas;
  esa key se usa solo en esa request y **no se guarda ni se loggea**.
- Las IPs se hashean antes de guardarse en Redis. No se loggean keys ni emails.

---

## Setup local

### 1. Backend (FastAPI)

Requisitos: Python 3.11+.

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium          # descarga el navegador

cp .env.example .env                 # y rellena los valores (ver abajo)
uvicorn app.main:app --reload --port 8000
```

Variables en `backend/.env`:

| Variable       | Qué es                                                    |
| -------------- | --------------------------------------------------------- |
| `YT_API_KEY`   | API key de YouTube Data API v3 (tuya, del dueño).         |
| `FRONTEND_URL` | URL del frontend para CORS (`http://localhost:3000`).     |
| `REDIS_URL`    | URL de conexión a Redis para el rate limit (opcional local). |

> Sin `REDIS_URL` configurada, el rate limit queda desactivado (modo dev). Está
> bien para probar localmente.

Verifica: `http://localhost:8000/health` → `{"status":"ok"}`.

### 2. Frontend (Next.js)

Requisitos: Node 18.18+.

```bash
cd frontend
npm install
cp .env.example .env.local           # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Abre `http://localhost:3000`.

---

## Deploy

### Backend → Render

1. Crea un servicio **Web Service** apuntando a este repo.
2. **Root Directory**: `backend`
3. **Build Command**:
   ```
   pip install -r requirements.txt && playwright install --with-deps chromium
   ```
4. **Start Command**:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. **Health Check Path**: `/health`
6. **Environment Variables**: `YT_API_KEY`, `FRONTEND_URL` (la URL de Vercel),
   `REDIS_URL`.

> El repo incluye `backend/render.yaml` (Blueprint) que ya define todo esto; puedes
> usar **New → Blueprint** en lugar de configurarlo a mano.

⚠️ El plan gratis de Render **duerme tras 15 min** de inactividad. La primera
búsqueda tras dormir puede tardar ~1 min (el frontend ya avisa de esto).

### Redis (rate limit)

Sirve cualquier Redis (Redis Cloud, Upstash, etc.). Solo necesitas una `REDIS_URL`:

1. En tu proveedor (ej. <https://app.redislabs.com> / Redis Cloud), abre tu base.
2. Pulsa **Connect → Redis client** y copia la cadena de conexión completa:
   ```
   redis://default:TU_PASSWORD@redis-XXXXX.cloud.redislabs.com:PUERTO
   ```
   (Si la base usa TLS, el esquema es `rediss://`.)
3. Pégala como env var `REDIS_URL` en Render (y en `backend/.env` para probar local).

### Frontend → Vercel

1. Importa el repo en Vercel.
2. **Root Directory**: `frontend`
3. **Environment Variable**: `NEXT_PUBLIC_API_URL` = la URL pública del backend de
   Render (ej. `https://scraper-yt-backend.onrender.com`).
4. Deploy. Luego actualiza `FRONTEND_URL` en Render con el dominio final de Vercel.

---

## Notas y límites

- **Cuota de YouTube**: cada `search` cuesta 100 unidades (de 10.000/día por key).
  Por eso el rate limit y la opción de key propia.
- **Email**: YouTube oculta muchos emails tras un CAPTCHA; solo se captan los que
  el creador deja visibles en la descripción o el `/about`. Las redes (IG/TikTok)
  suelen ser una vía de contacto más fiable.
- **Cap por búsqueda**: máx. 3 keywords y ~25 canales scrapeados por búsqueda para
  no exceder el timeout de Render. Ajustable en `backend/app/config.py`.

## Estructura

```
backend/   FastAPI + Playwright (deploy en Render)
frontend/  Next.js (deploy en Vercel)
scraper.py CLI original (referencia; no se usa en producción)
```
