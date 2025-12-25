---
title: OC P5 - API ML Déployée
emoji: 🎯
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
license: mit
---

# 🎯 Employee Turnover Prediction - DEV Environment

Interface Gradio pour tester le modèle de prédiction de départ des employés (turnover).

## 🚀 Modèle ML

- **Algorithme**: XGBoost optimisé avec RandomizedSearchCV
- **Équilibrage**: SMOTE pour gérer le déséquilibre de classes (ratio 5:1)
- **Tracking**: MLflow pour versioning et reproductibilité
- **Métriques**: F1-Score optimisé (0.51), Accuracy 79%
- **Stockage**: [Hugging Face Hub](https://huggingface.co/ASI-Engineer/employee-turnover-model)

## 📊 Fonctionnalités

- **Status Checker**: Vérifier l'état du modèle et les métriques
- **API Simple**: Interface Gradio pour tests rapides
- **Chargement automatique**: Modèle téléchargé depuis HF Hub au démarrage

## 🔧 Architecture

```python
# Chargement du modèle depuis HF Hub
model_path = hf_hub_download(
    repo_id="ASI-Engineer/employee-turnover-model",
    filename="model/model.pkl"
)
model = mlflow.sklearn.load_model(str(Path(model_path).parent))
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

# Lancer l'interface Gradio
poetry run python app.py
```

### Requirements.txt (automatique)

Le fichier `requirements.txt` est **généré automatiquement** par le CI/CD lors des déploiements sur HF Spaces.

**Vous n'avez rien à faire !** Modifiez juste `pyproject.toml` et le CI/CD s'occupe du reste.

Si vous voulez le générer manuellement :
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
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
