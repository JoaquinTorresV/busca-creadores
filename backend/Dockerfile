# Imagen oficial de Playwright para Python: ya trae Chromium + TODAS las
# librerías del sistema que el navegador necesita. La versión del tag DEBE
# coincidir con la de playwright en requirements.txt (1.49.1).
FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# 1) Dependencias de Python (capa cacheable)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Aseguramos el binario de Chromium para esta versión de Playwright.
#    (La imagen base ya lo incluye; esto es idempotente y rápido.)
RUN playwright install chromium

# 3) Código de la app
COPY . .

# Render inyecta el puerto en $PORT. Usamos shell form para que se expanda.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
