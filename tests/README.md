# Tests Structure

**Tests organisés** : 86 tests, 75.63% coverage

---

## 📂 Structure Organisée

```
tests/
├── conftest.py                 # Fixtures pytest partagées (client, DB, valid data)
├── test_api/                   # Tests API endpoints (5 fichiers, ~36 tests)
│   ├── __init__.py
│   ├── test_api_auth.py        # Tests authentification API Key
│   ├── test_api_demo.py        # Tests intégration API déployée (HF Spaces)
│   ├── test_api_health.py      # Tests endpoint /health
│   ├── test_api_predict.py     # Tests endpoint /predict (unitaire)
│   └── test_api_validation.py  # Tests validation Pydantic (schémas)
├── test_database/              # Tests base de données (1 fichier, ~7 tests)
│   ├── __init__.py
│   └── test_database.py        # Tests PostgreSQL (connexion, insertion, requêtes)
├── test_functional/            # Tests end-to-end (1 fichier, ~17 tests)
│   ├── __init__.py
│   └── test_functional.py      # Tests fonctionnels complets (prediction + DB + perf)
└── test_model/                 # Tests modèle ML (1 fichier, ~26 tests)
    ├── __init__.py
    └── test_model.py           # Tests chargement modèle, preprocessing, prédictions
```

---

## 🧪 Exécuter les Tests

### Tous les tests
```bash
poetry run pytest tests/ -v --cov
```

### Par catégorie
```bash
# Tests API uniquement
poetry run pytest tests/test_api/ -v

# Tests base de données
poetry run pytest tests/test_database/ -v

# Tests fonctionnels
poetry run pytest tests/test_functional/ -v

# Tests modèle ML
poetry run pytest tests/test_model/ -v
```

### Coverage HTML
```bash
poetry run pytest tests/ --cov=src --cov=api --cov-report=html:docs/coverage_report
```

---

## 📊 Métriques

| Catégorie | Nombre de Tests | Description |
|-----------|----------------|-------------|
| **API** | ~36 tests | Authentification, health, predict, validation |
| **Database** | ~7 tests | Connexion, CRUD, intégrité données |
| **Functional** | ~17 tests | End-to-end, performance, error handling |
| **Model** | ~26 tests | Chargement modèle, preprocessing, prédictions |
| **TOTAL** | **86 tests** | Coverage: **75.63%** |

---

## 🎯 Bonnes Pratiques Implémentées

✅ **Organisation modulaire** : Tests regroupés par catégorie (API, DB, ML)  
✅ **Fixtures centralisées** : conftest.py avec client, database, valid data  
✅ **Packages Python** : __init__.py dans chaque subdir  
✅ **Isolation** : Chaque catégorie testable indépendamment  
✅ **Nommage clair** : test_<catégorie>_<fonctionnalité>.py  
✅ **Coverage visible** : HTML report dans docs/coverage_report/

---

## 🔍 Fixtures Disponibles

Définies dans `conftest.py`:

| Fixture | Scope | Description |
|---------|-------|-------------|
| `client` | function | Client TestClient FastAPI |
| `database` | session | Connexion PostgreSQL (session-level) |
| `valid_employee_data` | function | Données employé valides (JSON) |
| `settings` | session | Configuration app (src.config) |

---

## 📝 Convention de Nommage

- **test_api_*.py** : Tests endpoints API REST
- **test_database.py** : Tests opérations base de données
- **test_functional.py** : Tests end-to-end complets
- **test_model.py** : Tests modèle ML (chargement, preprocessing, prédiction)

---

**Dernière mise à jour** : 2 janvier 2026  
**Pytest version** : 9.0.2  
**Coverage** : 75.63% (src/ + api.py)
