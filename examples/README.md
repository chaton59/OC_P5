# 📚 Exemples MLflow

Ce dossier contient des exemples pratiques pour utiliser MLflow dans le projet.

## 🚀 Exemples disponibles

### 1. Trouver le meilleur modèle
```bash
python examples/01_find_best_model.py
```
**Ce qu'il fait** :
- Liste les 5 meilleurs runs selon une métrique (cv_f1)
- Affiche les hyperparamètres et métriques du meilleur
- Charge le modèle pour vérifier qu'il fonctionne

**Utilisation** : Parfait pour identifier quel modèle utiliser dans ton API

---

### 2. Comparer plusieurs modèles
```bash
python examples/02_compare_models.py
```
**Ce qu'il fait** :
- Compare tous les runs d'une expérience
- Affiche un tableau avec métriques et hyperparamètres
- Génère un graphique de comparaison (si matplotlib installé)
- Calcule des statistiques (moyenne, max, min, écart-type)

**Utilisation** : Pour analyser tes expériences d'hyperparameter tuning

---

### 3. Gérer le Model Registry
```bash
python examples/03_model_registry.py
```
**Ce qu'il fait** :
- Liste tous les modèles enregistrés
- Affiche les versions et leurs stages
- Démontre comment promouvoir un modèle
- Charge un modèle depuis le Registry

**Utilisation** : Workflow de versioning pour la production

---

## 📖 Guide complet

Consulte `docs/mlflow_guide.md` pour :
- Architecture MLflow complète
- Intégration API FastAPI/Flask
- Best practices
- Workflow de retraining

## 🎯 Workflow recommandé

```bash
# 1. Entraîner plusieurs modèles
MLFLOW_TRACKING_URI=sqlite:///mlflow.db python tests/test_mlflow_quick.py

# 2. Trouver le meilleur
python examples/01_find_best_model.py

# 3. Comparer tous les runs
python examples/02_compare_models.py

# 4. Gérer le Registry
python examples/03_model_registry.py

# 5. Promouvoir en production (dans le code Python)
from mlflow.tracking import MlflowClient
client = MlflowClient()
client.transition_model_version_stage(
    name="XGBoost_Employee_Turnover",
    version=1,
    stage="Production"
)
```

## 🔗 Intégration API

Une fois le meilleur modèle identifié :

```python
import mlflow

# Option A : Charger par run_id
model = mlflow.sklearn.load_model("runs:/RUN_ID/model")

# Option B : Charger depuis le Registry
model = mlflow.sklearn.load_model("models:/XGBoost_Employee_Turnover/Production")

# Prédiction
predictions = model.predict(X_new)
```

## 💡 Tips

- **Métrique principale** : `cv_f1` (F1-score en cross-validation)
- **Métriques secondaires** : `test_precision`, `test_recall`, `test_f1`
- **Vérifier** : Que test_f1 ≈ cv_f1 (pas de surapprentissage)
- **Favoriser** : Modèles simples si performances similaires

## 🌐 MLflow UI

Pour visualiser graphiquement :
```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```
Puis ouvre http://localhost:5000
