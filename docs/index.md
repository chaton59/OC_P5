# Employee Turnover Prediction API

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.14-009688.svg)](https://fastapi.tiangolo.com)
[![Code Coverage](https://img.shields.io/badge/coverage-70.26%25-yellow.svg)](../htmlcov/index.html)
[![Tests](https://img.shields.io/badge/tests-97%20passed-success.svg)](../tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**API REST de prédiction du turnover des employés basée sur Machine Learning (XGBoost + SMOTE)**

[🔗 Demo Production](https://asi-engineer-oc-p5.hf.space){ .md-button .md-button--primary } 
[📚 Documentation API](API_GUIDE.md){ .md-button } 
[🐛 Report Bug](https://github.com/chaton59/OC_P5/issues){ .md-button }

</div>

---

## 📊 À Propos

Ce projet déploie un **modèle de Machine Learning** en production via une **API REST moderne** pour prédire le risque de départ des employés d'une entreprise. Développé dans le cadre du projet OpenClassrooms P5 "Déployez votre modèle de Machine Learning".

### Problématique

Les entreprises perdent des talents clés sans pouvoir anticiper. Ce modèle prédit le **risque de turnover** (probabilité qu'un employé quitte l'entreprise) à partir de 29 variables RH (satisfaction, salaire, ancienneté, etc.).

### Solution

API REST performante exposant un modèle **XGBoost optimisé** avec :

- ✅ **Validation robuste** des données via Pydantic
- ✅ **Prédictions en temps réel** (<2s) ou par batch (CSV)
- ✅ **Traçabilité complète** (PostgreSQL + logs structurés JSON)
- ✅ **Authentification sécurisée** (API Key)
- ✅ **CI/CD automatisé** (GitHub Actions → HuggingFace Spaces)

### Métriques du Modèle

| Métrique | Score | Interprétation |
|----------|-------|----------------|
| **F1 Score** | 0.85 | Excellent équilibre précision/recall |
| **Precision** | 0.82 | 82% des prédictions "va partir" sont correctes |
| **Recall** | 0.88 | 88% des vrais départs sont détectés |
| **ROC AUC** | 0.91 | Excellente capacité de discrimination |

!!! success "Performance"
    Le modèle détecte **88% des employés à risque** avec seulement **18% de faux positifs**.

---

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.12+
- Poetry 1.7+
- PostgreSQL 14+ (ou Docker)

### Installation en 3 étapes

```bash
# 1. Cloner le repo
git clone https://github.com/chaton59/OC_P5.git
cd OC_P5

# 2. Installer les dépendances
poetry install

# 3. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos credentials
```

### Lancer l'API

```bash
# Mode développement (sans auth)
poetry run uvicorn api:app --reload

# Accéder à la doc interactive
open http://localhost:8000/docs
```

!!! tip "Guides détaillés"
    - [Installation complète](installation.md)
    - [Configuration avancée](configuration.md)
    - [Premier déploiement](quickstart.md)

---

## 🏗️ Architecture

### Vue d'ensemble

```
┌─────────────┐
│   CLIENT    │ (curl, Python, JavaScript)
└──────┬──────┘
       │ HTTP/JSON
       ▼
┌─────────────────────────────────────┐
│         FASTAPI REST API            │
│  ┌──────────────────────────────┐   │
│  │ Authentication (API Key)     │   │
│  │ Rate Limiting (20 req/min)   │   │
│  │ Pydantic Validation (29 chps)│   │
│  └──────────────────────────────┘   │
└───────┬─────────────────────────────┘
        │
        ├──────────► ┌───────────────┐
        │            │  PostgreSQL   │ (Logs de prédictions)
        │            └───────────────┘
        │
        └──────────► ┌───────────────────────┐
                     │  MODÈLE ML (XGBoost)  │
                     │  ┌─────────────────┐  │
                     │  │ Preprocessing   │  │
                     │  │ Feature Eng     │  │
                     │  │ SMOTE Balance   │  │
                     │  │ XGBoost Predict │  │
                     │  └─────────────────┘  │
                     └───────────────────────┘
```

### Pipeline de Prédiction

1. **Réception des données** (JSON via POST)
2. **Validation Pydantic** (29 champs, contraintes strictes)
3. **Preprocessing** (scaling, encodage, features dérivées)
4. **Prédiction XGBoost** (probabilités classe 0/1)
5. **Niveau de risque** (Low/Medium/High selon seuils)
6. **Traçabilité** (log dans PostgreSQL)

!!! info "En savoir plus"
    - [Architecture détaillée du modèle](model/architecture.md)
    - [Guide de la base de données](database/guide.md)

---

## 📡 Endpoints Principaux

### 🏥 Health Check

```bash
GET /health
```

Vérifier que l'API et le modèle sont opérationnels.

### 🔮 Prédiction Unitaire

```bash
POST /predict
Content-Type: application/json
X-API-Key: your-key  # Requis en production

{
  "age": 35,
  "revenu_mensuel": 4500,
  "departement": "Commercial",
  "satisfaction_employee_nature_travail": 3,
  ...
}
```

### 📦 Prédiction Batch

```bash
POST /predict/batch
X-API-Key: your-key

# Upload de 3 fichiers CSV
sondage_file=@data/extrait_sondage.csv
eval_file=@data/extrait_eval.csv
sirh_file=@data/extrait_sirh.csv
```

!!! example "Exemples complets"
    Consultez le [guide API](api/guide.md) pour des exemples curl, Python et JavaScript.

---

## 🧪 Qualité du Code

### Tests

- **97 tests** (86 passés, 11 skippés pour déploiement)
- **70.26% de couverture** globale
- **9 catégories** : auth, validation, database, model, functional, API

```bash
# Exécuter les tests
poetry run pytest tests/ -v

# Avec rapport de couverture
poetry run pytest --cov=. --cov-report=html
```

### CI/CD Pipeline

GitHub Actions avec 4 jobs :

1. **Lint** (Black + Flake8) - ~30s
2. **Tests** (pytest + coverage) - ~3 min
3. **Test API Server** (health + predict) - ~2 min
4. **Deploy** (HF Spaces selon branche) - automatique

**Temps total** : ~5-7 minutes

---

## 🌐 Environnements

| Env | Branche | URL | Description |
|-----|---------|-----|-------------|
| **Production** | `main` | [asi-engineer-oc-p5.hf.space](https://asi-engineer-oc-p5.hf.space) | Stable, authentification requise |
| **Développement** | `dev` | [asi-engineer-oc-p5-dev.hf.space](https://asi-engineer-oc-p5-dev.hf.space) | Tests, auth désactivée |

---

## 📚 Documentation Complète

Cette documentation est organisée en sections :

- **[Guide de Démarrage](installation.md)** : Installation, configuration, premiers pas
- **[API](api/guide.md)** : Endpoints, authentification, exemples
- **[Modèle ML](model/technical.md)** : Architecture, performances, maintenance
- **[Déploiement](deployment/overview.md)** : HuggingFace, Docker, CI/CD
- **[Base de Données](database/guide.md)** : Schéma, migrations
- **[Tests](tests/strategy.md)** : Stratégie, couverture, exécution

---

## 🤝 Contribuer

Les contributions sont bienvenues ! Processus :

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📄 Licence

Projet développé dans un cadre pédagogique (OpenClassrooms).  
Les données utilisées sont fictives.

---

## 📚 Navigation Documentation

### 🚀 Guides de Démarrage

| Document | Description | Niveau |
|----------|-------------|--------|
| [Installation](installation.md) | Guide d'installation complet (Poetry, PostgreSQL, config) | **Débutant** |
| [Configuration](configuration.md) | Variables d'environnement (.env), secrets, modes | **Débutant** |
| [Quickstart](quickstart.md) | Démarrage rapide en 5 minutes | **Débutant** |

### 📖 Documentation API

| Document | Description | Pages |
|----------|-------------|-------|
| [API_GUIDE.md](API_GUIDE.md) | **Guide complet de l'API** (7 sections, exemples curl/Python/JS) | 980 lignes |

### 🤖 Documentation Modèle ML

| Document | Description | Pages |
|----------|-------------|-------|
| [MODEL_TECHNICAL.md](MODEL_TECHNICAL.md) | **Documentation technique du modèle** (architecture, métriques, maintenance) | 393 lignes |
| [TRAINING.md](TRAINING.md) | Guide d'entraînement du modèle (preprocessing, MLflow) | 148 lignes |

### 🚀 Déploiement & CI/CD

| Document | Description | Contenu |
|----------|-------------|---------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Guide déploiement (Docker, HF Spaces, GitHub Actions) | CI/CD pipeline |

### 🗄️ Base de Données

| Document | Description | Contenu |
|----------|-------------|---------|
| [database_guide.md](database_guide.md) | Guide PostgreSQL (création, insertion, requêtes) | Scripts SQL |

### 📊 Rapports & Inventaire

| Document | Description | Type |
|----------|-------------|------|
| [Coverage Report](coverage_report/index.html) | **Rapport de couverture des tests** (HTML interactif) | 70.27% |
| [DOCUMENTATION_INVENTORY.md](DOCUMENTATION_INVENTORY.md) | Inventaire complet de la documentation | Référence |
| [changelog.md](changelog.md) | Historique des versions et changements | Changelog |

### 🎓 Documents Pédagogiques (OpenClassrooms)

| Document | Description | Status |
|----------|-------------|--------|
| [ETAPE_6_COMPLETE.md](ETAPE_6_COMPLETE.md) | Rapport complet Étape 6 (documentation finale) | Terminé |
| [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) | Checklist de vérification projet | Validation |
| [etapes_archive.txt](etapes_archive.txt) | **Mission OpenClassrooms originale** (archivé) | Archive |

### 🧹 Rapports de Nettoyage

| Document | Description | Date |
|----------|-------------|------|
| [ETAT_PRE_SOUS_ETAPE_2.md](ETAT_PRE_SOUS_ETAPE_2.md) | État du projet avant nettoyage Phase 1 | 2 janv. 2026 |
| [SOUS_ETAPE_2_RAPPORT.md](SOUS_ETAPE_2_RAPPORT.md) | Rapport Sous-Étape 2: Validations | 2 janv. 2026 |
| [SOUS_ETAPE_3_RAPPORT.md](SOUS_ETAPE_3_RAPPORT.md) | Rapport Sous-Étape 3: Clean Racine | 2 janv. 2026 |
| [SOUS_ETAPE_4_RAPPORT.md](SOUS_ETAPE_4_RAPPORT.md) | Rapport Sous-Étape 4: Consolidation Docs | 2 janv. 2026 |

### 📋 MkDocs

| Document | Description | Rôle |
|----------|-------------|------|
| [README_MKDOCS.md](README_MKDOCS.md) | Guide utilisation MkDocs pour ce projet | Setup |

---

!!! tip "Navigation Optimale"
    - **Nouveaux utilisateurs** : Commencez par [Quickstart](quickstart.md)
    - **Développeurs** : Consultez [API_GUIDE.md](API_GUIDE.md) et [Coverage Report](coverage_report/index.html)
    - **Évaluateurs** : Voir [ETAPE_6_COMPLETE.md](ETAPE_6_COMPLETE.md) et rapports de nettoyage

---

## 📞 Contact

- **GitHub Issues** : [github.com/chaton59/OC_P5/issues](https://github.com/chaton59/OC_P5/issues)
- **Repository** : [github.com/chaton59/OC_P5](https://github.com/chaton59/OC_P5)

---

<div align="center">

**⭐ Si ce projet vous a aidé, n'hésitez pas à lui donner une étoile sur GitHub ! ⭐**

Made with ❤️ by [chaton59](https://github.com/chaton59)

</div>
