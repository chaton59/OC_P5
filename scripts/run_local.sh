#!/bin/bash
# Script de lancement local complet pour l'API Employee Turnover
set -e

# 1. Installer les dépendances si besoin
echo "[1/4] Installation des dépendances..."
poetry install

# 2. Vérifier le .env
if [ ! -f .env ]; then
  echo "[2/4] Copie du .env.example -> .env"
  cp .env.example .env
else
  echo "[2/4] Fichier .env déjà présent."
fi

# 3. Lancer l'interface Gradio
echo "[3/4] Lancement de l'interface Gradio..."
echo "Accès Gradio : http://localhost:7860"
poetry run python app.py
