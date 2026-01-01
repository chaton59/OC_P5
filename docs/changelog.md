# Changelog

Historique des versions du projet Employee Turnover Prediction API.

---

## v3.3.0 (Janvier 2026)

### 📚 Documentation (Étape 6 OpenClassrooms)

#### ✨ Nouvelles fonctionnalités documentation
- 📝 **13 nouveaux fichiers** de documentation créés (~5000 lignes)
- 🌐 **Site MkDocs** avec theme Material (17 pages HTML générées)
- 📊 **Inventaire complet** : DOCUMENTATION_INVENTORY.md (314 lignes)
- 🔧 **README restructuré** selon Best-README-Template (841 lignes)
- 📖 **Guide API exhaustif** : API_GUIDE.md (981 lignes, 7 exemples)
- 🤖 **Documentation technique modèle** : MODEL_TECHNICAL.md (393 lignes)
- 📈 **Visualisation performances** : model_performance.png (metrics + confusion matrix)
- ✅ **Vérification complète** : VERIFICATION_CHECKLIST.md

#### 📁 Structure MkDocs
- Configuration mkdocs.yml avec Material theme
- Pages créées : index, installation, configuration, quickstart, changelog
- Sections : API, Modèle ML, Déploiement, BDD, Tests
- Extensions : Admonitions, tabs, code highlighting, recherche française
- Build time : 0.70s, taille : ~3.5 MB

#### 🔗 Navigation et cohérence
- Liens internes vérifiés entre tous les documents
- URLs HuggingFace cohérentes (prod/dev)
- Métriques du modèle cohérentes (F1=0.85, etc.)
- Commandes d'installation testées

#### 📊 Livrables
- 6 commits documentés
- 5 sous-étapes complétées (inventaire, API, modèle, README, MkDocs)
- Instructions reproductibles validées
- Conformité 100% avec etapes.txt

---

## v3.2.1 (Janvier 2026)

### ✨ Nouvelles fonctionnalités
- 🎛️ Sliders Gradio et schémas Pydantic alignés sur les min/max réels des données d'entraînement
- 📦 Endpoint batch CSV (3 fichiers bruts)
- 🔑 Authentification API Key (production)

### 🔧 Corrections
- Correction preprocessing (scaling, ordre des colonnes)
- Fix de la validation Pydantic pour les contraintes

### 📝 Documentation
- Documentation complète enrichie (API_GUIDE, MODEL_TECHNICAL)
- Setup MkDocs avec theme Material
- Inventory complet de la documentation existante

---

## v2.2.0 (27 Décembre 2025)

### ✨ Nouvelles fonctionnalités
- 📦 Nouvel endpoint `/predict/batch` pour traitement CSV direct
- 📊 Amélioration précision des prédictions (~90%)

### 🔧 Corrections
- Fix preprocessing : ajout du scaling des features
- Fix preprocessing : correction de l'ordre des colonnes

---

## v2.1.0 (26 Décembre 2025)

### ✨ Nouvelles fonctionnalités
- ✨ Système de logging structuré JSON
- 🛡️ Rate limiting avec SlowAPI
- 📊 Monitoring des performances

### 🔧 Améliorations
- ⚡ Amélioration gestion d'erreurs
- 📝 Meilleurs messages d'erreur

---

## v2.0.0 (26 Décembre 2025)

### ✨ Nouvelles fonctionnalités
- ✅ Suite de tests complète (97 tests)
- 🔐 Authentification API Key
- 📊 70% de couverture de code

### 🏗️ Infrastructure
- CI/CD avec GitHub Actions (4 jobs)
- Déploiement automatique sur HuggingFace Spaces

---

## v1.0.0 (Décembre 2025)

### 🎉 Version initiale
- API REST FastAPI
- Modèle XGBoost + SMOTE
- Endpoints /health et /predict
- Base de données PostgreSQL
- Documentation Swagger/ReDoc
