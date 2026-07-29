# syntax=docker/dockerfile:1

# ---------- Etapa 1: build ----------
# Se usa una etapa separada solo para instalar dependencias con las
# herramientas de compilación necesarias (gcc, headers), que NO se
# necesitan en tiempo de ejecución. Esto reduce drásticamente el tamaño
# de la imagen final.
FROM python:3.12-slim AS builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ---------- Etapa 2: runtime ----------
# Imagen final: solo contiene el entorno virtual ya instalado (etapa
# anterior) y el código fuente. Ni compiladores ni cachés de pip.
FROM python:3.12-slim AS runtime

# Usuario no-root: buena práctica de seguridad, evita que un proceso
# comprometido dentro del contenedor tenga privilegios de root.
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

COPY . .

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Healthcheck: usa el endpoint /api/health que se implementa en la Fase 6.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:5000/api/health', timeout=2).status==200 else sys.exit(1)"

# Gunicorn en vez del servidor de desarrollo de Flask (run.py con
# app.run()), como corresponde en producción.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "run:app"]
