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
├── tests/                   # Suite pytest (84 tests, 75.12% couverture)
├── logs/                    # Logs JSON (NOUVEAU)
│   ├── api.log              # Tous les logs
│   └── error.log            # Erreurs uniquement
├── docs/                    # Documentation
├── ml_model/                # Scripts training
└── data/                    # Données sources
## 🗄️ Schéma de la Base de Données (PostgreSQL)

Schéma UML pour traçabilité ML (basé sur P5 prédiction turnover employé) :
![Schéma BDD](docs/schema.png)

- **dataset** : Dataset original (référence pour tests/retraining). Colonnes adaptées au modèle de prédiction turnover.
- **ml_logs** : Logs inputs/outputs (JSON pour flexibilité, timestamp pour audits).

Choix : Structure relationnelle pour efficacité volume data ; sécurité via user dédié (ml_user).
Instructions : Voir create_db.py pour création.

📖 **Guide complet pour débutants** : [docs/database_guide.md](docs/database_guide.md)

### 🖥️ Outils DB Visuels

Pour une gestion visuelle de la base de données PostgreSQL, utilisez DBeaver (recommandé pour la mission POC).

#### Installation de DBeaver
1. Téléchargez DBeaver Community depuis [dbeaver.io](https://dbeaver.io/download/).
2. Installez l'application sur votre système (Windows/Mac/Linux).

#### Configuration de la connexion PostgreSQL
1. Ouvrez DBeaver et cliquez sur "New Database Connection".
2. Sélectionnez "PostgreSQL" comme type de base de données.
3. Renseignez les paramètres de connexion :
   - **Host** : `localhost` (ou l'IP de votre serveur PostgreSQL)
   - **Port** : `5432` (port par défaut PostgreSQL)
   - **Database** : `oc_p5_db`
   - **Username** : `ml_user`
   - **Password** : Le mot de passe défini dans votre fichier `.env` (variable `DB_PASSWORD`)
4. Cliquez sur "Test Connection" pour vérifier.
5. Enregistrez la connexion.

#### Utilisation
- Explorez les tables `dataset` et `ml_logs`.
- Exécutez des requêtes SQL directement dans l'interface.
- Visualisez les données et les schémas.

### 💾 Insertion du Dataset
```bash
# Insérer le dataset complet (1470 employés)
poetry run python scripts/insert_dataset.py

# Vérifier l'insertion
psql -h localhost -U ml_user -d oc_p5_db -c "SELECT COUNT(*) FROM dataset;"
```

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

### Suite de tests complète

**Métriques** :
- ✅ **97 tests** (86 passés, 11 skippés pour déploiement)
- 📊 **70.26% de couverture** globale du code
- ⚡ Temps d'exécution : **~4 secondes**
- 🎯 **9 fichiers de tests** couvrant tous les aspects

### Catégories de tests

#### 🔐 Tests d'authentification (`test_api_auth.py`)
- Validation système d'authentification API Key
- Mode DEBUG vs Production
- Headers de sécurité
- Rate limiting par clé API
- **11 tests** - 100% passés

#### 🏥 Tests de santé (`test_api_health.py`)
- Endpoint `/health`
- Structure des réponses
- Statut du modèle
- Versionning
- **6 tests** - 100% passés

#### 🔮 Tests de prédiction (`test_api_predict.py`)
- Endpoint `/predict` avec données valides
- Structure des réponses (prediction, probabilities, risk_level)
- Validation des probabilités (somme = 1, range [0,1])
- Cohérence des prédictions
- **9 tests** - 100% passés

#### ✔️ Tests de validation (`test_api_validation.py`)
- Validation des champs requis
- Types de données
- Valeurs négatives
- Limites d'âge (18-70 ans)
- Énumérations (genre, département, statut_marital, etc.)
- Formats (augmentation_salaire en %)
- **15 tests** - 100% passés

#### 🗄️ Tests de base de données (`test_database.py`)
- Connexion PostgreSQL
- Existence des tables (`dataset`, `ml_logs`)
- Opérations CRUD
- Intégrité des contraintes
- **7 tests** - 100% passés

#### 🔄 Tests fonctionnels (`test_functional.py`)
- Tests end-to-end complets
- Intégration API + DB + Modèle ML
- Performance (temps de réponse < 2s)
- Gestion d'erreurs et rollback
- Scénarios de charge
- **19 tests** (17 passés, 2 skippés)

#### 🤖 Tests du modèle ML (`test_model.py`)
- Chargement depuis HuggingFace Hub
- Pipeline de preprocessing
- Feature engineering
- Validation Pydantic
- Prédictions réelles
- **23 tests** - 100% passés

#### 🌐 Tests d'intégration API déployée (`test_api_demo.py`)
- Tests sur API déployée HuggingFace Spaces
- Endpoints réels en production
- **7 tests** skippés en local (pour déploiement uniquement)

### Exécution des tests

```bash
# Tous les tests avec détails
poetry run pytest tests/ -v

# Avec couverture détaillée
poetry run pytest tests/ -v --cov=. --cov-report=term-missing

# Avec rapport HTML
poetry run pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html

# Tests spécifiques
poetry run pytest tests/test_api_predict.py -v
poetry run pytest tests/test_database.py -v

# Par catégorie (marqueurs)
poetry run pytest -m "not integration" -v  # Exclure tests d'intégration
```

### Détail de couverture par module

| Module | Couverture | Lignes | Manquantes |
|--------|------------|--------|------------|
| `src/config.py` | **100%** | 20 | 0 |
| `src/schemas.py` | **100%** | 100 | 0 |
| `src/rate_limit.py` | **100%** | 10 | 0 |
| `db_models.py` | **100%** | 14 | 0 |
| `src/logger.py` | **90.32%** | 62 | 6 |
| `src/preprocessing.py` | **76.36%** | 55 | 13 |
| `src/models.py` | **61.36%** | 44 | 17 |
| `api.py` | **55.41%** | 157 | 70 |
| `src/gradio_ui.py` | **52%** | 125 | 60 |
| `src/auth.py` | **47.37%** | 19 | 10 |

**Note** : Les modules avec couverture < 100% incluent des sections spécifiques au déploiement ou à Gradio UI (interface web), testées en environnement de production.

## 🚀 Déploiement

### Pipeline CI/CD automatisé

Le projet utilise **GitHub Actions** pour automatiser le workflow complet :

**Fichier** : `.github/workflows/ci-cd.yml`

**Workflow** (4 jobs séquentiels) :

1. **🔍 Lint** (~30s)
   - Black (formatage code)
   - Flake8 (qualité code)
   
2. **🧪 Tests** (~2-3 min)
   - pytest avec 97 tests
   - Couverture de code
   - Upload vers Codecov
   - Génération rapport HTML

3. **🚀 Test API Server** (~1-2 min)
   - Démarrage serveur uvicorn
   - Test endpoint `/health`
   - Test endpoint `/predict` avec payload réel
   - Validation des réponses

4. **📦 Deploy** (selon branche)
   - `dev` → HuggingFace Space `ASI-Engineer/oc_p5-dev`
   - `main` → HuggingFace Space `ASI-Engineer/oc_p5`

**⚡ Temps total** : ~5-7 minutes (< 10 min requis)

### Environnements

| Environnement | Branche | HF Space | URL |
|---------------|---------|----------|-----|
| **Développement** | `dev` | `oc_p5-dev` | https://asi-engineer-oc-p5-dev.hf.space |
| **Production** | `main` | `oc_p5` | https://asi-engineer-oc-p5.hf.space |

### Déploiement manuel

```bash
# 1. Vérifier que tous les changements sont commitées
git status

# 2. Push sur dev (déclenche CI/CD automatiquement)
git push origin dev

# 3. Vérifier le pipeline
# https://github.com/chaton59/OC_P5/actions

# 4. Tester sur l'espace dev
curl https://asi-engineer-oc-p5-dev.hf.space/health

# 5. Si OK, merger vers main (après validation)
git checkout main
git merge dev
git push origin main
```

### Configuration requise

**Secrets GitHub** (`Settings > Secrets and variables > Actions`) :
- `HF_TOKEN` : Token HuggingFace avec accès write
- `API_KEY` : Clé API pour les tests CI/CD

**Variables HF Spaces** (dans settings du Space) :
- `API_KEY` : Clé API production (sécurisée)
- `DEBUG` : `false` (production) / `true` (dev)
- `LOG_LEVEL` : `INFO`

### Documentation complète

📖 **Guide détaillé** : [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- Docker et containerisation
- Troubleshooting
- Monitoring et logs
- Rollback procedures

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
- ✅ Suite de tests complète (84 tests)
- 🔐 Authentification API Key
- 📊 88% de couverture de code

## 👥 Auteurs

- **Projet** : OpenClassrooms P5
- **Repo** : [github.com/chaton59/OC_P5](https://github.com/chaton59/OC_P5)
