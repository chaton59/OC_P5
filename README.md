---
title: OC P5 - API ML Déployée
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: static
app_file: app.py
pinned: false
---

# ML Deployment Project
Déploiement d'un modèle ML pour Futurisys : API FastAPI, PostgreSQL, tests Pytest, CI/CD.

## Aperçu
POC pour exposer un modèle ML via API performante, avec traçabilité DB et bonnes pratiques DevOps.

## Installation
1. Clone le repo : `git clone https://github.com/ton-username/ml-deployment-project.git`
2. Installe Poetry (si pas fait) : `curl -sSL https://install.python-poetry.org | python3 -`
3. Dépendances : `poetry install` (crée/lock .venv avec deps)
4. Active env : `poetry shell`

## Utilisation
- Dev : `poetry run uvicorn src.main:app --reload` (Étape 3 pour API).
- BDD : `poetry run python scripts/create_db.py` (Étape 4).
- Tests : `poetry run pytest` (Étape 5).

## Structure du Projet
- `src/` : Code core (API, modèle ML).
- `tests/` : Tests unitaires/fonctionnels (Pytest).
- `docs/` : Schémas UML, docs API.
- `scripts/` : Utils init (BDD, data load).
- `data/` : Datasets (ignorés pour privacy).

## CI/CD Optimization
- Pipelines configurés pour exécution <10 min (ex. : lint ~1 min, tests ~3 min, deploy ~2 min). Si >10 min, optimiser via cache Poetry ou jobs parallèles. Temps observés basés sur runs GitHub Actions.

## CI/CD Détails
- Pipeline : GitHub Actions pour lint (Flake8/Black), tests (Pytest), deploy HF.
- Environnements : Dev (branch dev/local tests), Prod (branch main/HF oc_p5).
- Secrets : HF_TOKEN sécurisé via GitHub Secrets.
- Standards : Voir [docs/standards.md](./docs/standards.md).

## Branches & Conventions
- `main` : Stable (merges via PR).
- `main` : pour développement et tests
- `feature/etapeX` : Fonctionnalités (kebab-case, ex. `feature/etape3-api`).
- Commits : Conventional (ex. `feat: Add endpoint`).

## Déploiement & Sécurité
- CI/CD : GitHub Actions (Étape 2) pour tests/deploy Hugging Face.
- Auth/Sec : À venir (JWT pour API, secrets en .env ignoré).
- Versions : Tags semver (ex. v1.0.0 pour Étape 1).

## HF Spaces
- Prod : https://huggingface.co/spaces/ASI-Engineer/oc_p5 (branch dev, pour tests itératifs).
- Sync auto via GitHub Actions (push déclenche rebuild ~2min, avec HF_TOKEN sécurisé).

## Documentation 
- Standards Code/ML

## Licence
MIT (ou adapte pour Futurisys).