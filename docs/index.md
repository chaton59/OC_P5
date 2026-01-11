# 🚀 Employee Turnover Prediction API

<div align="center">

**API de prédiction du turnover des employés avec Machine Learning**

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.127-009688.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/tests-97%20passed-success.svg)](../tests/)

[🔗 Demo](https://asi-engineer-oc-p5.hf.space){ .md-button .md-button--primary }
[📚 API Guide](api.md){ .md-button }
[🤖 Modèle](model.md){ .md-button }

</div>

---

## 📊 Présentation

API REST qui prédit le risque de départ d'un employé à partir de ses données RH (âge, salaire, satisfaction, etc.). 

**Modèle** : XGBoost avec SMOTE  
**Performance** : F1 Score 0.85 | Recall 88%  
**Dataset** : 1470 employés, 29 variables

### Fonctionnalités

- 🔮 **Prédiction unitaire** : JSON → probabilité de départ
- 📦 **Prédiction batch** : CSV → résultats complets
- 🔐 **Authentification** : API Key sécurisée
- 📊 **Traçabilité** : Logs PostgreSQL + JSON structuré
- 🎨 **Interface Gradio** : UI web interactive

---

## ⚡ Démarrage Rapide

```bash
# Installation
git clone https://github.com/chaton59/OC_P5.git
cd OC_P5
poetry install

# Configuration
cp .env.example .env
# Éditer DEBUG=true pour dev

# Lancer l'API
poetry run uvicorn api:app --reload
```

Accéder à : [http://localhost:8000/docs](http://localhost:8000/docs)

➡️ **Guide complet** : [Installation](installation.md)

---

## 🏗️ Architecture

```

**Pipeline** : Données → Validation → Preprocessing → XGBoost → Traçabilité

---

## 📡 Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Vérifier l'état de l'API |
| `/predict` | POST | Prédiction unitaire (JSON) |
| `/predict/batch` | POST | Prédiction batch (3 CSV) |
| `/docs` | GET | Documentation Swagger |
| `/ui` | GET | Interface Gradio |

➡️ **Guide détaillé** : [API](api.md)

---

## 📚 Documentation

| Section | Description |
|---------|-------------|
| [Installation](installation.md) | Setup complet (Poetry, PostgreSQL, .env) |
| [API](api.md) | Endpoints, authentification, exemples |
| [Modèle](model.md) | Architecture ML, métriques, features |
| [Entraînement](training.md) | Pipeline training, MLflow, hyperparamètres |
| [Déploiement](deployment.md) | HuggingFace Spaces, CI/CD, Docker |
| [Configuration](configuration.md) | Variables d'environnement, secrets |

---

## 🌐 Environnements

| Env | URL | Auth | Branche |
|-----|-----|------|---------|
| **Prod** | [asi-engineer-oc-p5.hf.space](https://asi-engineer-oc-p5.hf.space) | ✅ | `main` |
| **Dev** | [asi-engineer-oc-p5-dev.hf.space](https://asi-engineer-oc-p5-dev.hf.space) | ❌ | `dev` |

---

## 📊 Métriques

| Métrique | Valeur | Description |
|----------|--------|-------------|
| **F1 Score** | 0.85 | Équilibre précision/recall |
| **Recall** | 0.88 | Détecte 88% des départs |
| **Precision** | 0.82 | 82% des prédictions correctes |
| **ROC AUC** | 0.91 | Excellente discrimination |
| **Tests** | 97 | 86 passés, 70% coverage |

---

Projet OpenClassrooms P5 · [GitHub](https://github.com/chaton59/OC_P5) · [Issues](https://github.com/chaton59/OC_P5/issues)
