# 🚀 Guide MLflow - Projet Employee Turnover

## 📋 Table des matières
1. [Workflow complet MLflow](#workflow-complet)
2. [Comparer plusieurs runs](#comparer-runs)
3. [Trouver le meilleur modèle](#meilleur-modèle)
4. [Charger un modèle pour l'API](#api-integration)
5. [Best Practices](#best-practices)

---

## 1. Workflow complet MLflow

### 🎯 Concept clé
MLflow suit ce workflow :
```
Entraînement → Tracking → Registry → Déploiement → API
```

### Architecture actuelle du projet
```
train_model.py
    ↓ (log params/metrics/model)
mlflow.db (SQLite)
    ↓ (query)
MLflow UI (http://localhost:5000)
    ↓ (select best model)
Model Registry (XGBoost_Employee_Turnover)
    ↓ (load)
API FastAPI/Flask
    ↓ (serve)
Prédictions
```

---

## 2. Comparer plusieurs runs

### Scénario : Tester différents hyperparamètres

**Exemple : Tester 3 configurations différentes**

```python
# tests/test_multiple_runs.py
import mlflow
from ml_model.preprocess import preprocess_data
from ml_model.train_model import train_model

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("Hyperparameter_Tuning")  # Créer une expérience dédiée

# Chemins des données
data_paths = {
    "sondage_path": "data/extrait_sondage.csv",
    "eval_path": "data/extrait_eval.csv",
    "sirh_path": "data/extrait_sirh.csv",
}

# Préparer les données une seule fois
X, y, scaler, encoders = preprocess_data(data_paths)

# Tester 3 configurations
configs = [
    {"name": "Baseline", "n_iter": 100, "cv": 3},
    {"name": "Intensive", "n_iter": 500, "cv": 5},
    {"name": "Quick", "n_iter": 50, "cv": 3},
]

for config in configs:
    with mlflow.start_run(run_name=config["name"]):
        # Log la configuration testée
        mlflow.log_param("config_name", config["name"])
        mlflow.log_param("n_iter", config["n_iter"])
        mlflow.log_param("cv", config["cv"])
        
        # Entraîner (modifier train_model pour accepter n_iter/cv)
        model, params, cv_f1 = train_model(X, y)
        
        print(f"✅ {config['name']}: F1={cv_f1:.4f}")
```

**Résultat dans MLflow UI** :
- Va sur **Experiments** → **Hyperparameter_Tuning**
- Tu verras 3 runs avec leurs métriques côte à côte
- Clique sur **"Compare"** pour voir un tableau comparatif

---

## 3. Trouver le meilleur modèle

### Option A : Via l'API MLflow (recommandé pour l'API)

```python
# api/get_best_model.py
import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("sqlite:///mlflow.db")
client = MlflowClient()

def get_best_model_from_experiment(experiment_name="Default", metric="cv_f1"):
    """
    Trouve le meilleur modèle d'une expérience basé sur une métrique.
    
    Args:
        experiment_name: Nom de l'expérience MLflow
        metric: Métrique à optimiser (cv_f1, test_f1, etc.)
    
    Returns:
        run_id du meilleur modèle
    """
    # Récupérer l'expérience
    experiment = client.get_experiment_by_name(experiment_name)
    if not experiment:
        raise ValueError(f"Expérience '{experiment_name}' introuvable")
    
    # Rechercher tous les runs de l'expérience
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=[f"metrics.{metric} DESC"],  # Trier par métrique décroissante
        max_results=1  # Prendre seulement le meilleur
    )
    
    if not runs:
        raise ValueError(f"Aucun run trouvé dans l'expérience '{experiment_name}'")
    
    best_run = runs[0]
    print(f"🏆 Meilleur modèle trouvé:")
    print(f"   Run ID: {best_run.info.run_id}")
    print(f"   {metric}: {best_run.data.metrics.get(metric, 'N/A')}")
    print(f"   Date: {best_run.info.start_time}")
    
    return best_run.info.run_id

# Exemple d'utilisation
if __name__ == "__main__":
    best_run_id = get_best_model_from_experiment("Default", "cv_f1")
    
    # Charger le modèle
    model_uri = f"runs:/{best_run_id}/model"
    model = mlflow.sklearn.load_model(model_uri)
    print(f"✅ Modèle chargé : {type(model)}")
```

### Option B : Via le Model Registry (pour production)

```python
# api/load_production_model.py
import mlflow

mlflow.set_tracking_uri("sqlite:///mlflow.db")

def load_production_model(model_name="XGBoost_Employee_Turnover", stage="Production"):
    """
    Charge le modèle en production depuis le Model Registry.
    
    Args:
        model_name: Nom du modèle dans le Registry
        stage: Stage du modèle ("Staging", "Production", "Archived")
    
    Returns:
        Modèle chargé
    """
    model_uri = f"models:/{model_name}/{stage}"
    
    try:
        model = mlflow.sklearn.load_model(model_uri)
        print(f"✅ Modèle '{model_name}' ({stage}) chargé")
        return model
    except Exception as e:
        print(f"⚠️ Erreur : {e}")
        print(f"💡 Astuce : Promouvoir une version en '{stage}' dans MLflow UI")
        
        # Fallback : Charger la dernière version
        model_uri = f"models:/{model_name}/latest"
        model = mlflow.sklearn.load_model(model_uri)
        print(f"✅ Fallback : Dernière version chargée")
        return model

# Utilisation
if __name__ == "__main__":
    model = load_production_model()
```

---

## 4. API Integration - Exemple complet

### Créer une API Flask/FastAPI avec MLflow

```python
# api/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import pandas as pd
import numpy as np

# Configuration
mlflow.set_tracking_uri("sqlite:///mlflow.db")
app = FastAPI(title="Employee Turnover Prediction API")

# Charger le modèle au démarrage
MODEL_NAME = "XGBoost_Employee_Turnover"
model = None

@app.on_event("startup")
def load_model():
    global model
    try:
        # Charger le dernier modèle du Registry
        model_uri = f"models:/{MODEL_NAME}/latest"
        model = mlflow.sklearn.load_model(model_uri)
        print(f"✅ Modèle chargé : {MODEL_NAME}")
    except Exception as e:
        print(f"❌ Erreur chargement modèle : {e}")
        raise

# Schéma de requête
class PredictionRequest(BaseModel):
    features: list[float]  # Liste de 50 features (après prétraitement)
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": [0.5, 1.2, -0.3, 0.8] + [0.0] * 46  # 50 features
            }
        }

class PredictionResponse(BaseModel):
    prediction: int  # 0 ou 1
    probability: float  # Probabilité de départ (classe 1)
    model_version: str

# Endpoint de prédiction
@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Prédit si un employé va quitter l'entreprise.
    
    - **features**: Liste de 50 features numériques (après prétraitement)
    - Retourne la prédiction (0=reste, 1=part) et la probabilité
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    try:
        # Convertir en DataFrame
        X = pd.DataFrame([request.features])
        
        # Prédiction
        prediction = int(model.predict(X)[0])
        probability = float(model.predict_proba(X)[0][1])
        
        return PredictionResponse(
            prediction=prediction,
            probability=round(probability, 4),
            model_version=MODEL_NAME
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur prédiction : {str(e)}")

# Endpoint de santé
@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "model_name": MODEL_NAME
    }

# Endpoint pour lister les modèles disponibles
@app.get("/models")
def list_models():
    from mlflow.tracking import MlflowClient
    client = MlflowClient()
    
    models = []
    for rm in client.search_registered_models():
        latest_versions = rm.latest_versions
        models.append({
            "name": rm.name,
            "versions": len(latest_versions),
            "latest_version": latest_versions[0].version if latest_versions else None
        })
    
    return {"models": models}

# Lancer avec : uvicorn api.app:app --reload
```

**Tester l'API** :
```bash
# Installer FastAPI
pip install fastapi uvicorn

# Lancer le serveur
uvicorn api.app:app --reload --port 8000

# Tester
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [0.5, 1.2, -0.3] + [0.0] * 47}'
```

---

## 5. Best Practices

### ✅ Stratégie de versioning des modèles

```python
# Workflow recommandé
# 1. Entraîner plusieurs modèles → Experiment "Development"
# 2. Sélectionner le meilleur → Promouvoir en "Staging"
# 3. Valider en staging → Promouvoir en "Production"
# 4. API charge toujours "Production"

from mlflow.tracking import MlflowClient

client = MlflowClient()
model_name = "XGBoost_Employee_Turnover"

# Promouvoir version 2 en Production
client.transition_model_version_stage(
    name=model_name,
    version=2,
    stage="Production"
)
```

### 📊 Logging avancé

```python
# Dans train_model.py, ajouter plus de contexte
with mlflow.start_run():
    # Log dataset info
    mlflow.log_param("n_samples", len(X))
    mlflow.log_param("n_features", X.shape[1])
    mlflow.log_param("class_imbalance_ratio", sum(y==0)/sum(y==1))
    
    # Log artifacts (graphiques, etc.)
    import matplotlib.pyplot as plt
    
    # Confusion matrix plot
    plt.figure()
    # ... plot code ...
    plt.savefig("confusion_matrix.png")
    mlflow.log_artifact("confusion_matrix.png")
    
    # Log code version
    import subprocess
    git_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode()
    mlflow.set_tag("git_commit", git_commit)
```

### 🔄 Retraining workflow

```python
# scripts/retrain_model.py
import mlflow
from datetime import datetime

def retrain_and_compare():
    """Entraîne un nouveau modèle et le compare à la production."""
    
    # 1. Charger le modèle en production
    prod_model = mlflow.sklearn.load_model("models:/XGBoost_Employee_Turnover/Production")
    
    # 2. Entraîner nouveau modèle
    X, y, _, _ = preprocess_data(data_paths)
    new_model, params, new_f1 = train_model(X, y)
    
    # 3. Comparer les performances
    from sklearn.model_selection import cross_val_score
    prod_f1 = cross_val_score(prod_model, X, y, cv=5, scoring='f1').mean()
    
    print(f"Production F1: {prod_f1:.4f}")
    print(f"New model F1: {new_f1:.4f}")
    
    # 4. Si meilleur, promouvoir automatiquement
    if new_f1 > prod_f1:
        print("✅ Nouveau modèle meilleur ! Promotion en Staging...")
        # Enregistrer dans Registry
        # ... code de promotion ...
    else:
        print("⚠️ Nouveau modèle moins bon, conservation du modèle actuel")
```

---

## 📚 Ressources

- **MLflow Docs**: https://mlflow.org/docs/latest/index.html
- **Model Registry**: https://mlflow.org/docs/latest/model-registry.html
- **Python API**: https://mlflow.org/docs/latest/python_api/index.html

---

## 🎯 Prochaines étapes pour ton projet

1. ✅ **MLflow configuré** - Tracking local avec SQLite
2. ✅ **Modèle enregistré** - XGBoost_Employee_Turnover v1
3. 🔄 **TODO: Créer l'API** - FastAPI avec chargement du modèle
4. 🔄 **TODO: Tester comparaison** - Multiple runs avec hyperparams différents
5. 🔄 **TODO: CI/CD** - Auto-retraining et déploiement

**Commande pour démarrer l'API** :
```bash
# Créer api/app.py avec le code ci-dessus
uvicorn api.app:app --reload --port 8000
```
