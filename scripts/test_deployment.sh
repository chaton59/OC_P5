#!/bin/bash
# Script de test avant déploiement sur HuggingFace Spaces
# Vérifie que FastAPI et Gradio fonctionnent correctement ensemble

set -e

echo "=========================================="
echo "🧪 Test de l'application avant déploiement"
echo "=========================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de nettoyage
cleanup() {
    echo -e "\n${YELLOW}🧹 Nettoyage...${NC}"
    pkill -f "python app.py" 2>/dev/null || true
    pkill -f "uvicorn api:app" 2>/dev/null || true
    sleep 2
}

# Nettoyer avant de commencer
cleanup

# Trap pour nettoyer en cas d'interruption
trap cleanup EXIT INT TERM

echo -e "\n${YELLOW}1️⃣  Démarrage de l'application...${NC}"

# Chercher l'environnement virtuel
if [ -d ".venv" ]; then
    PYTHON=".venv/bin/python"
elif [ -d "venv" ]; then
    PYTHON="venv/bin/python"
else
    PYTHON="python3"
fi

echo -e "${YELLOW}   Using Python: $PYTHON${NC}"
$PYTHON app.py > /tmp/app_test.log 2>&1 &
APP_PID=$!

# Attendre le démarrage
echo -e "${YELLOW}⏳ Attente du démarrage (20s)...${NC}"
sleep 20

# Vérifier que le processus tourne
if ! ps -p $APP_PID > /dev/null; then
    echo -e "${RED}❌ L'application a crashé au démarrage${NC}"
    echo -e "\n${YELLOW}Logs:${NC}"
    tail -30 /tmp/app_test.log
    exit 1
fi

echo -e "${GREEN}✅ Application démarrée${NC}"

# Test 1: Health check FastAPI
echo -e "\n${YELLOW}2️⃣  Test health check FastAPI (port 8000)...${NC}"
if curl -s -f http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ FastAPI répond${NC}"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "{}"
else
    echo -e "${RED}❌ FastAPI ne répond pas${NC}"
    tail -30 /tmp/app_test.log
    exit 1
fi

# Test 2: Gradio home
echo -e "\n${YELLOW}3️⃣  Test interface Gradio (port 7860)...${NC}"
if curl -s -f http://localhost:7860/ > /dev/null; then
    echo -e "${GREEN}✅ Gradio répond${NC}"
else
    echo -e "${RED}❌ Gradio ne répond pas${NC}"
    tail -30 /tmp/app_test.log
    exit 1
fi

# Test 3: Prédiction API
echo -e "\n${YELLOW}4️⃣  Test prédiction via API FastAPI...${NC}"

# Récupérer la clé API depuis .env ou utiliser la clé par défaut
if [ -f ".env" ]; then
    API_KEY=$(grep "^API_KEY=" .env | cut -d'=' -f2)
else
    API_KEY="dev-key-change-me-in-production"
fi

RESPONSE=$(curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "nombre_participation_pee": 0,
    "nb_formations_suivies": 2,
    "nombre_employee_sous_responsabilite": 1,
    "distance_domicile_travail": 15,
    "niveau_education": 3,
    "domaine_etude": "Infra & Cloud",
    "ayant_enfants": "Y",
    "frequence_deplacement": "Occasionnel",
    "annees_depuis_la_derniere_promotion": 2,
    "annes_sous_responsable_actuel": 5,
    "satisfaction_employee_environnement": 3,
    "note_evaluation_precedente": 4,
    "niveau_hierarchique_poste": 2,
    "satisfaction_employee_nature_travail": 3,
    "satisfaction_employee_equipe": 3,
    "satisfaction_employee_equilibre_pro_perso": 2,
    "note_evaluation_actuelle": 4,
    "heure_supplementaires": "Non",
    "augementation_salaire_precedente": 5.5,
    "age": 35,
    "genre": "M",
    "revenu_mensuel": 4500.0,
    "statut_marital": "Marié(e)",
    "departement": "Commercial",
    "poste": "Manager",
    "nombre_experiences_precedentes": 3,
    "nombre_heures_travailless": 80,
    "annee_experience_totale": 10,
    "annees_dans_l_entreprise": 5,
    "annees_dans_le_poste_actuel": 2
  }')

if echo "$RESPONSE" | grep -q "prediction"; then
    echo -e "${GREEN}✅ Prédiction réussie${NC}"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
    echo -e "${RED}❌ Erreur lors de la prédiction${NC}"
    echo "$RESPONSE"
    exit 1
fi

# Test 4: Documentation Swagger
echo -e "\n${YELLOW}5️⃣  Test documentation Swagger...${NC}"
if curl -s -f http://localhost:8000/docs > /dev/null; then
    echo -e "${GREEN}✅ Documentation accessible${NC}"
else
    echo -e "${RED}❌ Documentation non accessible${NC}"
    exit 1
fi

# Résumé final
echo -e "\n=========================================="
echo -e "${GREEN}✅ TOUS LES TESTS SONT PASSÉS !${NC}"
echo -e "=========================================="
echo ""
echo "L'application est prête pour le déploiement sur HuggingFace Spaces."
echo ""
echo "Prochaines étapes :"
echo "1. Committez vos changements : git add . && git commit -m 'Deploy FastAPI + Gradio'"
echo "2. Poussez sur GitHub : git push origin main"
echo "3. HF Spaces se synchronisera automatiquement"
echo "4. Vérifiez les logs sur https://huggingface.co/spaces/votre-username/votre-space/logs"
echo ""
echo "URLs attendues sur HF Spaces :"
echo "  - Interface : https://votre-space.hf.space/"
echo "  - API interne : http://localhost:8000 (non publique)"
echo ""

# Nettoyer
cleanup

exit 0
