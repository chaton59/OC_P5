FROM python:3.12-slim

WORKDIR /app

# Installer Poetry
RUN pip install poetry

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances Poetry
COPY pyproject.toml poetry.lock ./

# Configurer Poetry pour ne pas créer d'environnement virtuel
RUN poetry config virtualenvs.create false

# Installer les dépendances Python via Poetry
RUN poetry install --no-dev --no-interaction --no-ansi

# Copier le code de l'application
COPY app.py .
COPY db_models.py .
COPY src/ ./src/
COPY .env.example .env

# Créer le dossier logs
RUN mkdir -p logs

# Exposer le port (7860 = Gradio par défaut sur HuggingFace Spaces)
EXPOSE 7860

# Variables d'environnement par défaut
ENV DEBUG=false
ENV LOG_LEVEL=INFO
ENV API_KEY=change-me-in-production

# Healthcheck - vérifier que FastAPI répond sur /health
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:7860/health || exit 1

# Commande de démarrage - FastAPI avec Gradio monté sur /ui
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
