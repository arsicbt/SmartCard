FROM python:3.11-slim

WORKDIR /app

# Dépendances système minimales (psycopg2, build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Le contexte de build est la racine du repo (voir render.yaml : rootDir non défini)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Backend/ .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# storage.reload() dans app.py crée les tables au démarrage (idempotent)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "120", "app:app"]