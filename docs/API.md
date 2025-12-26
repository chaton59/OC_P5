# 🚀 API Employee Turnover Prediction

API REST FastAPI pour prédire le risque de départ d'un employé.

## 📋 Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Informations sur l'API |
| GET | `/health` | Health check |
| GET | `/docs` | Documentation Swagger |
| GET | `/ui` | Interface Gradio |
| POST | `/predict` | Prédiction turnover |

## 🚀 Démarrage rapide

```bash
# Installation
poetry install

# Lancement (dev)
poetry run uvicorn app:app --reload

# Lancement (prod)
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2
```

**URLs disponibles :**
- API : http://localhost:8000
- Swagger : http://localhost:8000/docs
- Interface Gradio : http://localhost:8000/ui

## 🔐 Authentification

L'endpoint `/predict` est protégé par API Key en production (`DEBUG=False`).

### Configuration
```bash
# .env
API_KEY=votre-cle-secrete
DEBUG=False  # Active l'authentification
```

### Utilisation
```bash
curl -X POST http://localhost:8000/predict \
  -H "X-API-Key: votre-cle-secrete" \
  -H "Content-Type: application/json" \
  -d @employee.json
```

### Générer une clé
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📊 Exemple de requête

### Données d'entrée (format CSV brut)
```json
{
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
  "nombre_heures_travailless": 45,
  "annee_experience_totale": 10,
  "annees_dans_l_entreprise": 5,
  "annees_dans_le_poste_actuel": 2
}
```

### Réponse
```json
{
  "prediction": 0,
  "probability_0": 0.85,
  "probability_1": 0.15,
  "risk_level": "Low"
}
```

## 🔄 Preprocessing

Le preprocessing est appliqué automatiquement à chaque requête :

1. **Feature Engineering** : ratios (revenu/ancienneté), moyennes satisfaction
2. **Encoding** : OneHot (genre, département, poste...), Ordinal (fréquence déplacement)
3. **Scaling** : StandardScaler sur variables numériques

## ⚠️ Codes d'erreur

| Code | Description |
|------|-------------|
| 200 | Succès |
| 401 | API Key manquante ou invalide |
| 422 | Données invalides (validation Pydantic) |
| 429 | Rate limit dépassé (20 req/min) |
| 500 | Erreur serveur |

## 🧪 Tests

```bash
# Lancer tous les tests
poetry run pytest

# Avec couverture
poetry run pytest --cov=src --cov=app

# Tests spécifiques
poetry run pytest tests/test_api_predict.py -v
```

## 📁 Structure du code

```
src/
├── auth.py          # Authentification API Key
├── config.py        # Configuration (.env)
├── gradio_ui.py     # Interface Gradio
├── logger.py        # Logging JSON structuré
├── models.py        # Chargement modèle HF Hub
├── preprocessing.py # Pipeline de transformation
├── rate_limit.py    # Rate limiting SlowAPI
└── schemas.py       # Schémas Pydantic
```
