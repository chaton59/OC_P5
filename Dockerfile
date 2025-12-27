FROM python:3.12-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY app.py .
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
ENV GRADIO_SERVER_PORT=7860

# Healthcheck - vérifier que le port répond (Gradio répond avec 200 sur /config)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:7860/config || curl -f http://localhost:7860/ || exit 1

# Commande de démarrage - Gradio standalone (fonctionne mieux sur HF Spaces)
CMD ["python", "-c", "from src.gradio_ui import launch_standalone; launch_standalone()"]
