# d:\Freelance\Python_Dev\Pwa\Dockerfile
# Build l'image Docker pour exécuter Django via Gunicorn.
# Assure un déploiement stable et reproductible en entreprise.
# RELEVANT FILES:docker-compose.yml, Devis/settings.py, requirements.txt, nginx/default.conf

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libcairo2 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

CMD ["gunicorn", "Devis.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
