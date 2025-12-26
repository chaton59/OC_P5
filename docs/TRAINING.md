# 🎓 Entraînement du modèle

Guide pour (ré)entraîner le modèle de prédiction du turnover.

## 📋 Vue d'ensemble

Le pipeline d'entraînement utilise :
- **XGBoost** : Algorithme de boosting performant
- **SMOTE** : Rééquilibrage des classes
- **MLflow** : Tracking des expériences
- **RandomizedSearchCV** : Optimisation hyperparamètres

## 🚀 Lancer l'entraînement

```bash
# Avec les données par défaut (data/*.csv)
python main.py
```

## 📁 Données requises

3 fichiers CSV dans `data/` :

| Fichier | Description |
|---------|-------------|
| `extrait_sondage.csv` | Données sondage satisfaction |
| `extrait_eval.csv` | Données évaluation performance |
| `extrait_sirh.csv` | Données administratives RH |

### Colonnes attendues

**Sondage :**
- `code_sondage`, `a_quitte_l_entreprise` (cible)
- `nombre_participation_pee`, `nb_formations_suivies`
- `distance_domicile_travail`, `niveau_education`
- `domaine_etude`, `ayant_enfants`, `frequence_deplacement`

**Évaluation :**
- `eval_number`, `satisfaction_employee_*`
- `note_evaluation_precedente`, `note_evaluation_actuelle`
- `heure_supplementaires`, `augementation_salaire_precedente`

**SIRH :**
- `id_employee`, `age`, `genre`, `revenu_mensuel`
- `statut_marital`, `departement`, `poste`
- `annees_dans_l_entreprise`, `annee_experience_totale`

## 🔄 Pipeline de preprocessing

Le fichier `ml_model/preprocess.py` :

1. **Chargement** : Merge des 3 CSV sur `employee_id`
2. **Nettoyage** : 
   - Parse `augementation_salaire_precedente` ("11 %" → 11.0)
   - Winsorize outliers (1%)
3. **Feature Engineering** :
   - `revenu_par_anciennete`
   - `experience_par_anciennete`
   - `promo_par_anciennete`
   - `satisfaction_moyenne`
4. **Encoding** :
   - OneHot : `genre`, `statut_marital`, `departement`, `poste`, `domaine_etude`
   - Ordinal : `frequence_deplacement` (Aucun < Occasionnel < Frequent)
5. **Scaling** : StandardScaler

## 🏋️ Entraînement

Le fichier `ml_model/train_model.py` :

```python
# Hyperparamètres optimisés via RandomizedSearchCV
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.2],
    'subsample': [0.8, 0.9, 1.0],
}

# Pipeline avec SMOTE
pipeline = Pipeline([
    ('smote', SMOTE(random_state=42)),
    ('xgb', XGBClassifier())
])

# Cross-validation
cv_results = cross_val_score(pipeline, X, y, cv=5, scoring='f1')
```

## 📊 MLflow Tracking

Après l'entraînement :

```bash
# Démarrer l'UI MLflow
mlflow ui --backend-store-uri sqlite:///mlflow.db

# Ouvrir http://localhost:5000
```

### Métriques loggées
- F1 Score (CV)
- Precision, Recall
- ROC AUC
- Confusion Matrix

### Artifacts sauvegardés
- `model.pkl` : Modèle entraîné
- `scaler.joblib` : StandardScaler
- `onehot_encoder.joblib` : OneHotEncoder
- `ordinal_encoder.joblib` : OrdinalEncoder

## 📦 Déployer le modèle

### 1. Uploader sur HuggingFace Hub

```python
from huggingface_hub import HfApi

api = HfApi()
api.upload_file(
    path_or_fileobj="model.pkl",
    path_in_repo="model/model.pkl",
    repo_id="ASI-Engineer/employee-turnover-model",
    repo_type="model"
)
```

### 2. L'API charge automatiquement
L'API télécharge le modèle depuis HF Hub au démarrage.

## 📈 Résultats actuels

| Métrique | Valeur |
|----------|--------|
| F1 Score (CV) | ~0.85 |
| Precision | ~0.82 |
| Recall | ~0.88 |
| ROC AUC | ~0.91 |

## 🔄 Ré-entraînement

Pour améliorer le modèle :

1. Ajouter des données dans `data/`
2. Modifier les hyperparamètres dans `ml_model/train_model.py`
3. Relancer `python main.py`
4. Comparer dans MLflow
5. Uploader le meilleur modèle sur HF Hub
