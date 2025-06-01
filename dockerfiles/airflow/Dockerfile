FROM apache/airflow:2.8.1

# ─── 1. Cambiamos a root para instalar paquetes del sistema ───────────────
USER root

# Dependencias necesarias para que Playwright funcione
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libxss1 \
    libasound2 \
    libxshmfence1 \
    libgbm1 \
    libgtk-3-0 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ─── 2. Volvemos a usuario airflow para instalar paquetes Python ─────────
USER airflow

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

# Instalar navegadores Playwright (sin --with-deps, ya instalamos deps)
RUN playwright install
