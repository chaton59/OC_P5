---
title: OC P5 - API ML Déployée
emoji: 🎯
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
license: mit
---

# 🎯 Employee Turnover Prediction - API FastAPI

API REST production-ready pour prédire le risque de départ des employés (turnover).

## 🚀 Quick Start

```bash
# 1. Cloner et installer
git clone https://github.com/chaton59/OC_P5.git
cd OC_P5
poetry install

# 2. Configurer l'API key (optionnel en dev)
cp .env.example .env
# Éditer .env et mettre votre API_KEY

# 3. Lancer l'API
poetry run uvicorn app:app --reload

# 4. Tester
curl http://localhost:8000/health
# Ouvrir http://localhost:8000/docs
```

## 📡 Utilisation de l'API

### Endpoints disponibles

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/` | GET | Informations API | ❌ |
| `/health` | GET | Health check | ❌ |
| `/predict` | POST | Prédiction turnover | ✅ API Key |
| `/docs` | GET | Documentation Swagger | ❌ |

### Exemple de prédiction

```bash
# Avec API Key (production)
curl -X POST http://localhost:8000/predict \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "genre": "M",
    "revenu_mensuel": 3500.0,
    "satisfaction_employee_environnement": 2,
    "annees_dans_l_entreprise": 5,
    ...
  }'

# Réponse
{
  "prediction": 1,
  "probability_0": 0.35,
  "probability_1": 0.65,
  "risk_level": "High"
}
```

### 🔒 Authentification

L'API utilise une **API Key** simple via header HTTP :

```bash
# Header requis en production
X-API-Key: your-secret-api-key
```

**Configuration :**
1. Copiez `.env.example` vers `.env`
2. Générez une clé : `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. Mettez `API_KEY=votre-cle-generee` dans `.env`
4. En dev, mettez `DEBUG=True` pour désactiver l'auth

**Pourquoi une API Key ?**
- ✅ Protège l'endpoint `/predict` contre les abus
- ✅ Permet de tracker qui utilise l'API
- ✅ Facile à révoquer/changer
- ✅ Compatible avec tous les clients HTTP

**Limitations (à améliorer) :**
- ⚠️ Pas de rate limiting (à venir)
- ⚠️ Pas de gestion des quotas
- ⚠️ Pas d'authentification OAuth2 (simplicité volontaire)

## 🏗️ Architecture

## 🚀 Modèle ML

- **Algorithme**: XGBoost optimisé avec RandomizedSearchCV
- **Équilibrage**: SMOTE pour gérer le déséquilibre de classes (ratio 5:1)
- **Tracking**: MLflow pour versioning et reproductibilité
- **Métriques**: F1-Score optimisé (0.51), Accuracy 79%
- **Stockage**: [Hugging Face Hub](https://huggingface.co/ASI-Engineer/employee-turnover-model)

## 📊 Fonctionnalités

### ✅ Implémenté (Étape 3 complète)

- **API REST complète** : 3 endpoints opérationnels
- **Validation Pydantic** : 30+ champs avec types, ranges, enums
- **Authentification** : API Key via header HTTP (`.env`)
- **Preprocessing automatique** : Feature engineering + encoding + scaling
- **Documentation interactive** : Swagger UI (`/docs`) + ReDoc (`/redoc`)
- **Health check** : Monitoring du statut API + modèle
- **CORS configuré** : Prêt pour frontend
- **Chargement lazy** : Modèle chargé au démarrage (cache)

### 🚧 À venir (Étapes suivantes)

- **PostgreSQL** : Logging des prédictions (étape 4)
- **Tests unitaires** : Couverture endpoints + preprocessing
- **Rate limiting** : Protection contre abus
- **Dockerfile** : Déploiement containerisé

## 🏗️ Architecture

```
app.py                   # API FastAPI principale
├── src/
│   ├── models.py       # Chargement modèle depuis HF Hub ✅
│   ├── schemas.py      # Validation Pydantic (30+ features) ✅
│   ├── preprocessing.py# Pipeline preprocessing ✅
│   ├── auth.py         # Authentification API Key ✅
│   └── config.py       # Configuration (.env) ✅
├── ml_model/           # Code d'entraînement MLflow
│   ├── preprocess.py
│   └── train_model.py
└── data/               # Datasets
```

**Pipeline de prédiction :**
```
Données employé (JSON)
  ↓ Validation Pydantic
  ↓ Vérification API Key
  ↓ Feature Engineering
  ↓ Encoding + Scaling
  ↓ Modèle XGBoost + SMOTE
  ↓ Prédiction + Probabilités
Réponse JSON
```

## 🛠️ Installation & Développement

### Prérequis
- Python 3.12+
- Poetry (gestionnaire de dépendances)

### Installation avec Poetry

```bash
# Installer Poetry (si pas déjà fait)
curl -sSL https://install.python-poetry.org | python3 -

# Installer les dépendances
poetry install

# Activer l'environnement virtuel
poetry shell

# Lancer le pipeline d'entraînement
poetry run python main.py

# Lancer l'API FastAPI
poetry run uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Configuration

```bash
# Copier le template de configuration
cp .env.example .env

# Générer une API key forte
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Éditer .env et configurer
nano .env
```

**Variables importantes :**
- `API_KEY` : Clé secrète pour `/predict`
- `DEBUG=True` : Désactive l'auth en dev
- `HF_MODEL_REPO` : Repository du modèle HF Hub

### Tests et Linting

```bash
# Formater le code
poetry run black .

# Linter
poetry run flake8 .
```

## 📈 Métriques

- **F1-Score**: 0.5136
- **Accuracy**: 79%
- **Données**: 1470 échantillons, 50 features
- **Classes**: {0: 1233, 1: 237} - Ratio 5.20:1

## 🔗 Liens

- **Documentation API complète** : [`docs/API_GUIDE.md`](docs/API_GUIDE.md)
- **GitHub** : [chaton59/OC_P5](https://github.com/chaton59/OC_P5)
- **Modèle HF Hub** : [ASI-Engineer/employee-turnover-model](https://huggingface.co/ASI-Engineer/employee-turnover-model)
- **CI/CD** : GitHub Actions (linting automatique)

## 📝 Notes techniques

### Modèle ML
- Pipeline : SMOTE + XGBClassifier
- Features : 50+ après preprocessing
- Optimisation : RandomizedSearchCV
- Tracking : MLflow local (`mlruns/`)

### API
- Framework : FastAPI 0.115+
- Validation : Pydantic v2
- Auth : API Key simple (header HTTP)
- ASGI Server : Uvicorn

### Développement
- Package manager : Poetry
- Python : 3.12+
- Linting : Black + Flake8
- Git workflow : `dev` → `main`
