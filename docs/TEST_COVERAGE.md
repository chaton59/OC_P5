# Test Coverage Report

## 📊 Résumé

- **Tests exécutés** : 33 passés, 3 skippés
- **Couverture globale** : **88%**
- **Lignes couvertes** : 389 / 443 statements

## 📈 Détail par module

| Module | Statements | Missing | Coverage |
|--------|------------|---------|----------|
| `src/schemas.py` | 74 | 1 | **99%** ✅ |
| `src/preprocessing.py` | 38 | 2 | **95%** ✅ |
| `src/config.py` | 19 | 0 | **100%** ✅ |
| `app.py` | 58 | 15 | **74%** |
| `src/models.py` | 47 | 20 | **57%** |
| `src/auth.py` | 19 | 13 | **32%** ⚠️ |

## ✅ Tests par catégorie

### 🏥 Health Check (6 tests)
- ✅ Status code 200
- ✅ Structure JSON
- ✅ Status "healthy"
- ✅ Modèle chargé
- ✅ Version présente
- ✅ Content-Type JSON

### 🔮 Prédiction Success (9 tests)
- ✅ Endpoint fonctionne
- ✅ Structure réponse
- ✅ Valeurs prédiction (0/1)
- ✅ Probabilités somment à 1
- ✅ Probabilités entre 0-1
- ✅ Risk level valide
- ✅ Employé haut risque
- ✅ Content-Type JSON
- ✅ Consistance prédictions

### ❌ Validation Errors (13 tests)
- ✅ Champs manquants → 422
- ✅ Types incorrects → 422
- ✅ Valeurs négatives → 422
- ✅ Âge < 18 ans → 422
- ✅ Âge > 70 ans → 422
- ✅ Genre invalide → 422
- ✅ Département invalide → 422
- ✅ Statut marital invalide → 422
- ✅ Fréquence déplacement invalide → 422
- ✅ Structure erreur FastAPI
- ✅ JSON vide → 422
- ✅ Revenu < 1000€ → 422
- ✅ Formations > 10 → 422

### 🔐 Authentification (5 + 3 manuels)
- ✅ Système d'auth configuré
- ✅ Mode DEBUG bypass auth
- ✅ Module auth import
- ✅ Module config import
- ✅ Header X-API-Key configuré
- ⏭️ Tests production (manuels)

## 🎯 Zones non couvertes

### `src/auth.py` (32% - Critique)
**Lignes manquantes** : Logique d'authentification en production

**Raison** : Tests tournent en mode DEBUG=True
- `verify_api_key()` avec clé invalide
- HTTPException 401 sans clé
- HTTPException 401 avec mauvaise clé

**Solution** : Tests manuels documentés dans `test_api_auth.py`

### `src/models.py` (57%)
**Lignes manquantes** : Error handling du chargement modèle
- Exception si HF Hub inaccessible
- Exception si fichier modèle corrompu

### `app.py` (74%)
**Lignes manquantes** : 
- Exception handling health check
- CORS configuration
- Lifespan shutdown

## 🚀 Comment lancer les tests

```bash
# Tous les tests
poetry run pytest tests/ -v

# Avec couverture
poetry run pytest tests/ --cov --cov-report=html

# Tests spécifiques
poetry run pytest tests/test_api_health.py -v
poetry run pytest tests/test_api_predict.py -v
poetry run pytest tests/test_api_validation.py -v

# Voir rapport HTML
open htmlcov/index.html
```

## ✅ Validation

Ce rapport démontre que :
1. **L'API est robuste** : 33 tests automatisés
2. **La validation fonctionne** : 13 tests d'erreurs
3. **Les prédictions sont fiables** : Tests de cohérence
4. **Le code est couvert à 88%** : Niveau excellent

Les 12% non couverts sont majoritairement du error handling
(situations exceptionnelles difficiles à simuler en tests unitaires).
