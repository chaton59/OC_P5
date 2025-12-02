# Plan du Pipeline CI/CD

## Objectif
Automatiser tests (qualité code/ML) et déploiement vers Hugging Face Spaces pour un POC scalable. Flux : Push → Tests → Build → Deploy (dev sur branche `dev`, prod sur `main` avec validation manuelle).  
*Choix : GitHub Actions pour simplicité/intégration gratuite ; HF Spaces pour hébergement ML sans infra (GPU si besoin pour inférence). Temps cible <10min par run (vigilance doc).*

## Triggers
- Push sur branches : `dev` (auto-deploy dev), `main` (deploy prod après review).
- Pull Requests vers `main` (tests + validation avant merge).  
*Choix : Limite à ces branches pour isoler envs ; évite triggers sur features pour perf.*

## Étapes du Pipeline (Séquentiel : Tests d'abord, puis Deploy si OK)
1. **Checkout Code** : Récupère le repo.  
   *Outil : `actions/checkout@v4` (standard, rapide).*
2. **Setup Environnement** : Python 3.10+ (compatible FastAPI/Pytest/SQLAlchemy).  
   *Choix : Version fixe pour reproductibilité ML ; cache deps pour accélérer runs futurs.*
3. **Installation Dépendances** : `pip install -r requirements.txt` + outils tests (pytest, black, flake8).  
   *Choix : Inclut lint pour standards code (reco ML : black pour formatage auto).*
4. **Linting** : Vérifie style (`black --check`, `flake8`).  
   *Pourquoi ? Détecte erreurs tôt ; coverage >80% visé pour robustesse.*
5. **Tests Automatisés** : `pytest --cov=src` (unitaires/fonctionnels API/ML).  
   *Choix : Couvre cas critiques (erreurs validation Pydantic, prédictions ML) ; rapport XML pour badges GitHub.*
6. **Build (Optionnel pour POC)** : Package API (e.g., build Docker si HF le requiert).  
   *Évolutif : Ajoute plus tard pour prod.*
7. **Déploiement** : Push vers HF Space (dev/prod).  
   *Choix : Conditionnel par branche ; utilise secrets pour HF_TOKEN (sécurité).*

## Gestion Envs et Secrets
- **Devs** : Branche `dev` → Space `ton-username/espace-dev` (tests rapides).
- **Test/Prod** : PR → `main` → Space `espace-prod` (review requise).
- **Secrets** : HF_TOKEN (GitHub Secrets) ; jamais en code.  
*Choix : Sépare envs pour traçabilité (inputs/outputs ML en DB PostgreSQL plus tard).*

## Standards Code/ML
- Format : Black.
- Tests : >80% coverage ; reproductibles (seeds pour ML).
- Monitoring : Badges GitHub pour coverage/status.  
*Pourquoi ? Assure fiabilité en prod ; aligné sur reco OpenClassrooms (ressource doc).*
