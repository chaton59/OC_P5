FROM python:3.12-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier de dépendances (généré via poetry export)
COPY requirements.txt .

# Installer les dépendances Python directement via pip
# Cette approche est plus robuste que poetry install sur HF Spaces
RUN pip install --no-cache-dir -r requirements.txt

# Vérifier que les dépendances critiques sont bien installées
RUN python -c "import slowapi; import fastapi; import gradio; print('✓ All critical dependencies installed')"

# Copier le code de l'application
COPY app.py .
COPY api.py .
COPY db_models.py .
COPY src/ ./src/

# Créer le dossier logs
RUN mkdir -p logs

# Exposer les ports (7860 = Gradio, 8000 = FastAPI)
EXPOSE 7860 8000

# Variables d'environnement par défaut
ENV DEBUG=false
ENV LOG_LEVEL=INFO
ENV API_KEY=change-me-in-production
ENV PYTHONUNBUFFERED=1

# Healthcheck - vérifier que Gradio répond
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
  CMD curl -f http://localhost:7860/ || exit 1

# Commande de démarrage
CMD ["python", "app.py"]
