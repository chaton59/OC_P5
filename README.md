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

# 🎯 Employee Turnover Prediction - DEV Environment

API FastAPI pour le modèle de prédiction de départ des employés (turnover).

## 🚀 Modèle ML

- **Algorithme**: XGBoost optimisé avec RandomizedSearchCV
- **Équilibrage**: SMOTE pour gérer le déséquilibre de classes (ratio 5:1)
- **Tracking**: MLflow pour versioning et reproductibilité
- **Métriques**: F1-Score optimisé (0.51), Accuracy 79%
- **Stockage**: [Hugging Face Hub](https://huggingface.co/ASI-Engineer/employee-turnover-model)

## 📊 Fonctionnalités (En développement - Étape 3)

- **API REST**: Endpoints FastAPI pour les prédictions
- **Validation**: Schémas Pydantic pour valider les données entrantes
- **Documentation**: Swagger/OpenAPI automatique
- **Chargement automatique**: Modèle et preprocessing artifacts depuis MLflow

## 🔧 Architecture

```python
# À IMPLÉMENTER - Étape 3
# Chargement du modèle depuis MLflow
# + Preprocessing artifacts (scaler, encoders)
# + Endpoints FastAPI avec validation Pydantic
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

# Lancer l'API FastAPI (à implémenter)
# poetry run uvicorn app:app --reload
```

### Requirements.txt

Le fichier `requirements.txt` contient les dépendances pour FastAPI et le modèle ML.

Pour le générer manuellement :
```bash
./scripts/export_requirements.sh
```

### Tests et Linting

```bash
# Formater le code
poetry run black .

# Linter
poetry run flake8 .

# Tests
poetry run pytest --cov=ml_model tests/
```

## 📈 Métriques

- **F1-Score**: 0.5136
- **Accuracy**: 79%
- **Données**: 1470 échantillons, 50 features
- **Classes**: {0: 1233, 1: 237} - Ratio 5.20:1

## 🔗 Liens

- **Modèle**: [employee-turnover-model](https://huggingface.co/ASI-Engineer/employee-turnover-model)
- **GitHub**: [OC_P5](https://github.com/chaton59/OC_P5)
- **CI/CD**: GitHub Actions avec déploiement automatique

Ce Space est synchronisé automatiquement via CI/CD depuis la branche `dev` du repository GitHub.

**Repository**: [chaton59/OC_P5](https://github.com/chaton59/OC_P5)
