# 🚀 API FastAPI - Employee Turnover Prediction

API REST complète pour prédire le risque de départ d'un employé.

## 📋 Architecture

```
OC_P5/
├── app.py                    # Application FastAPI principale
├── src/
│   ├── models.py            # Chargement modèle depuis HF Hub
│   ├── schemas.py           # Schémas Pydantic (validation)
│   └── preprocessing.py     # Pipeline de preprocessing
├── ml_model/                 # Code d'entraînement
├── test_api.py              # Script de test
└── requirements.txt         # Dépendances
```

## 🎯 Endpoints

### `GET /`
Informations sur l'API.

### `GET /health`
Health check - Status de l'API et du modèle.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_type": "Pipeline",
  "version": "1.0.0"
}
```

### `POST /predict`
Prédiction du turnover d'un employé.

**Request body:** (30+ champs - voir `/docs` pour le schéma complet)
```json
{
  "nombre_participation_pee": 0,
  "nb_formations_suivies": 0,
  "age": 41,
  "genre": "F",
  "revenu_mensuel": 5993.0,
  ...
}
```

**Response:**
```json
{
  "prediction": 1,
  "probability_0": 0.35,
  "probability_1": 0.65,
  "risk_level": "High"
}
```

## 🚀 Démarrage

### Installation
```bash
poetry install
```

### Lancement
```bash
# Avec Poetry
poetry run uvicorn app:app --reload

# Ou directement
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

L'API sera disponible sur : http://localhost:8000

## 📖 Documentation

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

Documentation interactive avec possibilité de tester directement les endpoints.

## 🧪 Tests

### Test rapide
```bash
python test_api.py
```

### Test avec curl
```bash
# Health check
curl http://localhost:8000/health

# Prédiction (exemple minimal)
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @test_data.json
```

## 🔧 Validation Pydantic

Tous les champs sont strictement validés :
- **Types** : int, float, str, enum
- **Ranges** : ge (>=), le (<=)
- **Enums** : valeurs prédéfinies (genre, département, etc.)

En cas d'erreur de validation, l'API retourne un **422 Unprocessable Entity** avec détails.

## 📊 Features (30+ colonnes)

### Données Sondage
- `nombre_participation_pee`, `nb_formations_suivies`
- `distance_domicile_travail`, `niveau_education`
- `domaine_etude`, `frequence_deplacement`
- ...

### Données Evaluation
- `satisfaction_employee_*` (environnement, nature travail, équipe, pro/perso)
- `note_evaluation_precedente`, `note_evaluation_actuelle`
- `heure_supplementaires`, `augementation_salaire_precedente`
- ...

### Données SIRH
- `age`, `genre`, `revenu_mensuel`, `statut_marital`
- `departement`, `poste`
- `annees_dans_l_entreprise`, `annee_experience_totale`
- ...

## 🎨 Preprocessing

Le preprocessing est appliqué automatiquement :
1. **Feature Engineering** : ratios, moyennes
2. **Encoding** : OneHot (catégorielles), Ordinal (fréquence)
3. **Scaling** : StandardScaler (numériques)

## 🔄 Modèle

- **Source** : HF Hub `ASI-Engineer/employee-turnover-model`
- **Type** : Pipeline(SMOTE + XGBClassifier)
- **Chargement** : Au démarrage de l'API (cache)
- **Version** : MLflow tracking

## 📝 Exemple complet

Voir `test_api.py` pour un exemple de données complètes.

## ⚠️ Notes

- Le modèle est chargé **une seule fois** au démarrage (cache)
- Les artifacts de preprocessing sont recréés à chaque requête
- **TODO** : Sauvegarder et charger les encoders/scaler depuis MLflow

## 🚀 Prochaines étapes

1. Intégration PostgreSQL (étape 4) pour logging des prédictions
2. Tests unitaires des endpoints
3. Déploiement Docker/HF Spaces
4. Load testing et optimisation
