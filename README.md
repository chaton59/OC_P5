# 🚀 Employee Turnover Prediction API - v3.2.1

## 📊 Vue d'ensemble

API REST de prédiction du turnover des employés basée sur un modèle XGBoost avec SMOTE.


**✨ Nouveautés v3.2.1** :
- 🎛️ Sliders Gradio et schémas Pydantic alignés sur les min/max réels des données d'entraînement
- 📦 Endpoint batch CSV (3 fichiers bruts)
- 🔑 Authentification API Key (prod)
- 🔧 Correction preprocessing (scaling, ordre des colonnes)
- 📝 Documentation et exemples mis à jour

## 🏗️ Architecture

```
OC_P5/
├── app.py                    # Point d'entrée FastAPI
├── src/
│   ├── auth.py              # Authentification API Key
│   ├── config.py            # Configuration centralisée
│   ├── logger.py            # Logging structuré (NOUVEAU)
│   ├── models.py            # Chargement modèle HF Hub
│   ├── preprocessing.py     # Pipeline preprocessing
│   ├── rate_limit.py        # Rate limiting (NOUVEAU)
│   └── schemas.py           # Validation Pydantic
├── tests/                   # Suite pytest (33 tests, 88% couverture)
├── logs/                    # Logs JSON (NOUVEAU)
│   ├── api.log              # Tous les logs
│   └── error.log            # Erreurs uniquement
├── docs/                    # Documentation
├── ml_model/                # Scripts training
└── data/                    # Données sources
```

## 🚀 Installation

### Prérequis
- Python 3.12+
- Poetry 1.7+
- Git

### Setup rapide

```bash
# 1. Cloner le repo
git clone https://github.com/chaton59/OC_P5.git
cd OC_P5

# 2. Installer les dépendances
poetry install

# 3. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# 4. Lancer l'API
poetry run uvicorn app:app --reload

# 5. Accéder à la documentation
# http://localhost:8000/docs
```

## 📝 Configuration (.env)

```bash
# Mode développement (désactive auth + active logs détaillés)
DEBUG=true

# API Key (requis en production)
API_KEY=your-secret-key-here

# Logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# HuggingFace Model
HF_MODEL_REPO=ASI-Engineer/employee-turnover-model
MODEL_FILENAME=model/model.pkl
```

## 🔒 Authentification

### Mode DEBUG (développement)
```bash
# L'API Key n'est PAS requise
curl http://localhost:8000/predict -H "Content-Type: application/json" -d '{...}'
```

### Mode PRODUCTION
```bash
# L'API Key est REQUISE
curl http://localhost:8000/predict \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{...}'
```


## 📡 Endpoints

### 🏥 Health Check
```bash
GET /health

# Réponse
{
  "status": "healthy",
  "model_loaded": true,
  "model_type": "Pipeline",
  "version": "3.2.1"
}
```

### 🔮 Prédiction unitaire
```bash
POST /predict
Content-Type: application/json
X-API-Key: your-key (en production)

# Payload (exemple, contraintes réelles appliquées)
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
  "nombre_heures_travailless": 80,
  "annee_experience_totale": 10,
  "annees_dans_l_entreprise": 5,
  "annees_dans_le_poste_actuel": 2
}

# Réponse
{
  "prediction": 0,                    # 0 = reste, 1 = part
  "probability_0": 0.85,              # Probabilité de rester
  "probability_1": 0.15,              # Probabilité de partir
  "risk_level": "Low"                 # Low, Medium, High
}
```

### 📦 Prédiction batch (CSV)
```bash
POST /predict/batch
X-API-Key: your-key (en production)

# Envoi des 3 fichiers CSV bruts
curl -X POST "http://localhost:8000/predict/batch" \
  -H "X-API-Key: your-key" \
  -F "sondage_file=@data/extrait_sondage.csv" \
  -F "eval_file=@data/extrait_eval.csv" \
  -F "sirh_file=@data/extrait_sirh.csv"

# Réponse
{
  "total_employees": 1470,
  "predictions": [
    {"employee_id": 1, "prediction": 1, "probability_leave": 0.84, "risk_level": "High"},
    {"employee_id": 2, "prediction": 0, "probability_leave": 0.11, "risk_level": "Low"}
  ],
  "summary": {
    "total_stay": 1169,
    "total_leave": 301,
    "high_risk_count": 222,
    "medium_risk_count": 233,
    "low_risk_count": 1015
  }
}
```

## 📊 Logging

### Logs structurés JSON

**Fichiers** :
- `logs/api.log` : Tous les logs
- `logs/error.log` : Erreurs uniquement

**Format** :
```json
{
  "timestamp": "2025-12-26T10:30:45",
  "level": "INFO",
  "logger": "employee_turnover_api",
  "message": "Request POST /predict",
  "method": "POST",
  "path": "/predict",
  "status_code": 200,
  "duration_ms": 23.45,
  "client_host": "127.0.0.1"
}
```

## 🛡️ Rate Limiting

**Configuration** :
- **Développement** : Désactivé (DEBUG=true)
- **Production** : 20 requêtes/minute par IP ou API Key

**En cas de dépassement** :
```json
{
  "error": "Rate limit exceeded",
  "message": "20 per 1 minute"
}
```

## ✅ Tests

```bash
# Tous les tests
poetry run pytest tests/ -v

# Avec couverture
poetry run pytest tests/ --cov --cov-report=html

# Voir rapport HTML
open htmlcov/index.html
```

**Résultats** :
- ✅ 33 tests passés
- 📊 88% de couverture globale

## 🚀 Déploiement

### Variables d'environnement requises
```bash
DEBUG=false
API_KEY=<votre-clé-sécurisée>
LOG_LEVEL=INFO
```

### HuggingFace Spaces
Prêt pour déploiement avec `app.py` et `requirements.txt`

## 📚 Documentation

- **API Interactive** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **Guide complet** : [docs/API_GUIDE.md](docs/API_GUIDE.md)
- **Standards** : [docs/standards.md](docs/standards.md)
- **Couverture tests** : [docs/TEST_COVERAGE.md](docs/TEST_COVERAGE.md)

## 📦 Dépendances principales

- **FastAPI** 0.115.14 : Framework web
- **Pydantic** 2.12.5 : Validation données
- **XGBoost** 2.1.3 : Modèle ML
- **SlowAPI** 0.1.9 : Rate limiting
- **python-json-logger** 4.0.0 : Logs structurés
- **pytest** 9.0.2 : Tests


## 🔄 Changelog

### v3.2.1 (janvier 2026)
- 🎛️ Sliders Gradio et schémas Pydantic alignés sur les min/max réels des données d'entraînement
- 📦 Endpoint batch CSV (3 fichiers bruts)
- 🔑 Authentification API Key (prod)
- 🔧 Correction preprocessing (scaling, ordre des colonnes)
- 📝 Documentation et exemples mis à jour

### v2.2.0 (27 décembre 2025)
- 📦 Nouvel endpoint `/predict/batch` pour traitement CSV direct
- 🔧 Fix preprocessing : ajout du scaling des features
- 🔧 Fix preprocessing : correction de l'ordre des colonnes
- 📊 Amélioration précision des prédictions (~90%)

### v2.1.0 (26 décembre 2025)
- ✨ Système de logging structuré JSON
- 🛡️ Rate limiting avec SlowAPI
- ⚡ Amélioration gestion d'erreurs
- 📊 Monitoring des performances

### v2.0.0 (26 décembre 2025)
- ✅ Suite de tests complète (36 tests)
- 🔐 Authentification API Key
- 📊 88% de couverture de code

## 👥 Auteurs

- **Projet** : OpenClassrooms P5
- **Repo** : [github.com/chaton59/OC_P5](https://github.com/chaton59/OC_P5)
