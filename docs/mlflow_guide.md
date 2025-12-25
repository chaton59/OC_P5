# 🚀 Guide MLflow - Projet Employee Turnover

## 📋 Table des matières
1. [Workflow complet MLflow](#workflow-complet)
2. [Comparer plusieurs runs](#comparer-runs)
3. [Trouver le meilleur modèle](#meilleur-modèle)
4. [Model Registry](#model-registry)
5. [Best Practices](#best-practices)

---

## 1. Workflow complet MLflow

### 🎯 Concept clé
MLflow suit ce workflow :
```
Entraînement → Tracking → Registry → Sélection du meilleur modèle
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
    ↓ (versions & stages)
Modèle prêt pour déploiement
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

### Via l'API MLflow

```python
# examples/find_best_model.py (déjà créé dans le projet)
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
        order_by=[f"metrics.{metric} DESC"],
        max_results=1
    )
    
    if not runs:
        raise ValueError(f"Aucun run trouvé dans l'expérience '{experiment_name}'")
    
    best_run = runs[0]
    print(f"🏆 Meilleur modèle trouvé:")
    print(f"   Run ID: {best_run.info.run_id}")
    print(f"   {metric}: {best_run.data.metrics.get(metric, 'N/A')}")
    
    return best_run.info.run_id

# Charger le modèle
best_run_id = get_best_model_from_experiment("Default", "cv_f1")
model_uri = f"runs:/{best_run_id}/model"
model = mlflow.sklearn.load_model(model_uri)
```

---

## 4. Model Registry

### Gérer les versions de modèles

```python
# examples/model_registry.py (déjà créé dans le projet)
from mlflow.tracking import MlflowClient

client = MlflowClient()
model_name = "XGBoost_Employee_Turnover"

# Lister les versions
versions = client.search_model_versions(f"name='{model_name}'")
for v in versions:
    print(f"Version {v.version}: {v.current_stage}")

# Promouvoir en Production
client.transition_model_version_stage(
    name=model_name,
    version=1,
    stage="Production",
    archive_existing_versions=True
)

# Charger depuis le Registry
model = mlflow.sklearn.load_model(f"models:/{model_name}/Production")
```

---

## 5. Best Practices

### ✅ Stratégie de versioning des modèles

```python
# Workflow recommandé
# 1. Entraîner plusieurs modèles → Experiment "Development"
# 2. Sélectionner le meilleur → Promouvoir en "Staging"
# 3. Valider en staging → Promouvoir en "Production"

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
    
    # Log artifacts (graphiques)
    import matplotlib.pyplot as plt
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
    else:
        print("⚠️ Nouveau modèle moins bon, conservation du modèle actuel")
```

---

## 📚 Ressources

- **MLflow Docs**: https://mlflow.org/docs/latest/index.html
- **Model Registry**: https://mlflow.org/docs/latest/model-registry.html
- **Python API**: https://mlflow.org/docs/latest/python_api/index.html

---

## 🎯 Utilisation du projet

### Entraîner un modèle
```bash
python ml_model/train_model.py
```

### Lancer MLflow UI
```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

### Exemples disponibles
```bash
# Trouver le meilleur modèle
python examples/01_find_best_model.py

# Comparer tous les runs
python examples/02_compare_models.py

# Gérer le Model Registry
python examples/03_model_registry.py
```
