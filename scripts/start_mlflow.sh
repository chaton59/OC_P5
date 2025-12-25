#!/bin/bash
# Script pour démarrer MLflow UI et ouvrir le navigateur
# Usage: ./scripts/start_mlflow.sh

set -e

echo "🔍 Vérification du port 5000..."

# Tuer tous les processus MLflow
pkill -9 -f "mlflow ui" 2>/dev/null || true

# Tuer le port 5000 si occupé
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 5000 occupé, arrêt des processus..."
    kill -9 $(lsof -t -i:5000) 2>/dev/null || true
    sleep 2
fi

echo "✅ Port 5000 libre"
echo ""
echo "🚀 Démarrage de MLflow UI..."
echo "   Backend: sqlite:///mlflow.db"
echo "   Port: 5000"
echo ""

# Démarrer MLflow UI en arrière-plan
nohup .venv/bin/mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000 > mlflow_ui.log 2>&1 &

# Attendre que le serveur soit prêt
echo "⏳ Attente du démarrage du serveur..."
sleep 3

# Vérifier que le serveur est bien lancé
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "✅ MLflow UI démarré avec succès !"
    echo ""
    echo "📊 Interface accessible sur: http://localhost:5000"
    echo "📝 Logs disponibles dans: mlflow_ui.log"
    echo ""
    echo "🌐 Ouverture du navigateur..."
    
    # Ouvrir le navigateur selon l'OS
    if command -v xdg-open > /dev/null; then
        xdg-open http://localhost:5000
    elif command -v gnome-open > /dev/null; then
        gnome-open http://localhost:5000
    elif command -v open > /dev/null; then
        open http://localhost:5000
    else
        echo "⚠️  Impossible d'ouvrir automatiquement le navigateur"
        echo "   Ouvrez manuellement: http://localhost:5000"
    fi
    
    echo ""
    echo "💡 Pour arrêter MLflow UI:"
    echo "   pkill -f 'mlflow ui'"
    echo "   ou: fuser -k 5000/tcp"
else
    echo "❌ Erreur: MLflow UI n'a pas démarré correctement"
    echo "   Consultez mlflow_ui.log pour plus de détails"
    exit 1
fi
