#!/bin/bash
#
# 🚀 Script de lancement de l'API locale pour la démo
#
# Usage: ./lancer_api.sh
#

cd "$(dirname "$0")/.."

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  🚀 Lancement de l'API Employee Turnover                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Vérifier que poetry est installé
if ! command -v poetry &> /dev/null; then
    echo "❌ poetry n'est pas installé"
    echo "   Installation : pip install poetry"
    exit 1
fi

# Vérifier que le fichier api.py existe
if [ ! -f "api.py" ]; then
    echo "❌ Fichier api.py introuvable"
    echo "   Assurez-vous d'être dans le bon dossier"
    exit 1
fi

echo "✅ Démarrage de l'API sur http://127.0.0.1:7860"
echo ""
echo "📖 Documentation disponible sur:"
echo "   - http://127.0.0.1:7860/docs (Swagger)"
echo "   - http://127.0.0.1:7860/redoc (ReDoc)"
echo ""
echo "🔮 Interface Gradio (si activée):"
echo "   - http://127.0.0.1:7860/"
echo ""
echo "💡 Pour arrêter l'API : Ctrl+C"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Lancer l'API avec poetry en mode DEBUG (sans API key)
DEBUG=True poetry run uvicorn api:app --host 127.0.0.1 --port 7860
