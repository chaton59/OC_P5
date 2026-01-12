# 🎯 Employee Turnover Prediction API

Bienvenue dans la documentation de l'API de prédiction du turnover des employés.

## 📋 À propos du projet

Ce projet fournit une API de Machine Learning pour prédire le risque de départ des employés. Il utilise un modèle XGBoost entraîné sur des données RH.

## 🚀 Fonctionnalités

- **Prédiction individuelle** : Évaluez le risque de départ d'un employé
- **Prédiction par lot** : Traitez plusieurs employés en une seule requête
- **Interface Gradio** : Interface web interactive pour les démonstrations
- **API REST** : Endpoints FastAPI documentés avec Swagger/ReDoc

## 🔗 Liens rapides

| Section | Description |
|---------|-------------|
| [Documentation API](api_documentation.md) | Endpoints, authentification, exemples |
| [Architecture](architecture.md) | Structure du projet et composants |
| [Base de données](database_setup.md) | Configuration et schéma de la BDD |
| [Déploiement](deployment_guide.md) | Guide de déploiement sur HuggingFace Spaces |
| [Tests](tests_report.md) | Rapport de couverture et tests |

## 📦 Installation rapide

```bash
# Cloner le repo
git clone https://github.com/chaton59/OC_P5.git
cd OC_P5

# Installer les dépendances
poetry install

# Lancer l'API
poetry run uvicorn api:app --reload

# Lancer l'interface Gradio
poetry run python app.py
```

## 🌐 URLs de Production

| Service | URL |
|---------|-----|
| **Gradio (Prod)** | [asi-engineer-oc-p5.hf.space](https://asi-engineer-oc-p5.hf.space) |
| **API Docs** | [/docs](https://asi-engineer-oc-p5.hf.space/docs) |

## 📊 Stack technique

- **Backend** : FastAPI + Uvicorn
- **Frontend** : Gradio 6.2.0
- **ML** : XGBoost + scikit-learn
- **Base de données** : SQLite + SQLAlchemy
- **CI/CD** : GitHub Actions → HuggingFace Spaces
- **Documentation** : MkDocs Material

## 📝 Licence

Projet OpenClassrooms P5 - Data Scientist © 2026
