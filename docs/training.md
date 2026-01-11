# 🎓 Entraînement du Modèle

Guide pour entraîner ou ré-entraîner le modèle de prédiction du turnover.

---

## 📋 Vue d'Ensemble

**Pipeline** : Preprocessing → SMOTE → XGBoost → MLflow  
**Durée** : ~10-15 minutes  
**Output** : Modèle + encoders + métriques

---

## 🚀 Lancement

```bash
# Avec les données par défaut
poetry run python ml_model/main.py

# Le script enchaîne automatiquement :
# 1. Chargement et préprocessing
# 2. Training XGBoost avec RandomizedSearchCV
# 3. Logging dans MLflow
# 4. Sauvegarde des artifacts
```

---

## 📁 Données Requises

3 fichiers CSV dans `data/` :

| Fichier | Description | Colonnes Clés |
|---------|-------------|---------------|
| `extrait_sondage.csv` | Sondage satisfaction | `code_sondage`, `a_quitte_l_entreprise`, satisfactions |
| `extrait_eval.csv` | Évaluations performance | `eval_number`, notes, heures sup, promotions |
| `extrait_sirh.csv` | Données administratives | `id_employee`, âge, salaire, ancienneté |

### Format Attendu

**Sondage** :
- `code_sondage`, `a_quitte_l_entreprise` (cible : Oui/Non)
- `nombre_participation_pee`, `nb_formations_suivies`
- `distance_domicile_travail`, `niveau_education`
- `domaine_etude`, `ayant_enfants`, `frequence_deplacement`

**Évaluation** :
- `eval_number`, `satisfaction_employee_environnement`
- `satisfaction_employee_nature_travail`, `satisfaction_employee_equilibre_pro_perso`
- `satisfaction_employee_relation_hierarchique`
- `note_evaluation_precedente`, `note_evaluation_actuelle`
- `heure_supplementaires`, `augementation_salaire_precedente`

**SIRH** :
- `id_employee`, `age`, `genre`, `revenu_mensuel`
- `statut_marital`, `departement`, `poste`
- `annees_dans_l_entreprise`, `annee_experience_totale`

---

## 🔄 Pipeline de Preprocessing

Le fichier `ml_model/preprocess.py` effectue :

### 1. Chargement et Fusion

```python
# Merge des 3 CSV sur employee_id
df = pd.merge(sondage, eval, on='code')
df = pd.merge(df, sirh, on='id')
```

### 2. Nettoyage

```python
# Parse augmentation salaire : "11 %" → 11.0
df['augementation_salaire'] = df['augementation_salaire'].str.replace('%', '').astype(float)

# Winsorize outliers (1% de chaque côté)
from scipy.stats.mstats import winsorize
df['revenu'] = winsorize(df['revenu'], limits=[0.01, 0.01])
```

### 3. Feature Engineering

```python
# Ratios normalisés par ancienneté
df['revenu_par_anciennete'] = df['revenu'] / (df['anciennete'] + 1)
df['experience_par_anciennete'] = df['exp_totale'] / (df['anciennete'] + 1)
df['promo_par_anciennete'] = df['annees_promo'] / (df['anciennete'] + 1)

# Agrégat satisfaction
satisfaction_cols = [
    'satisfaction_employee_environnement',
    'satisfaction_employee_nature_travail',
    'satisfaction_employee_equilibre_pro_perso',
    'satisfaction_employee_relation_hierarchique'
]
df['satisfaction_moyenne'] = df[satisfaction_cols].mean(axis=1)
```

### 4. Encoding

```python
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

# OneHot : variables non-ordonnées
onehot = OneHotEncoder(handle_unknown='ignore')
onehot.fit_transform(df[['genre', 'statut_marital', 'departement', 'poste', 'domaine_etude']])

# Ordinal : fréquence déplacement
ordinal = OrdinalEncoder(categories=[['Aucun', 'Occasionnel', 'Frequent']])
ordinal.fit_transform(df[['frequence_deplacement']])
```

### 5. Scaling

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

---

## 🏋️ Entraînement

Le fichier `ml_model/train_model.py` :

### Configuration

```python
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV

# Pipeline avec SMOTE
pipeline = Pipeline([
    ('smote', SMOTE(random_state=42)),
    ('xgb', XGBClassifier(random_state=42))
])

# Hyperparamètres à tester
param_grid = {
    'xgb__n_estimators': [100, 200, 300, 500, 1000],
    'xgb__max_depth': [3, 5, 7, 10, 15],
    'xgb__learning_rate': [0.001, 0.01, 0.1, 0.2, 0.5],
    'xgb__subsample': [0.4, 0.6, 0.8, 0.9, 1.0],
    'xgb__colsample_bytree': [0.5, 0.7, 0.9, 1.0],
    'xgb__reg_alpha': [0, 0.5, 1, 2, 3],
    'xgb__gamma': [0, 1, 2, 5, 10]
}

# RandomizedSearchCV
search = RandomizedSearchCV(
    pipeline,
    param_distributions=param_grid,
    n_iter=1000,
    cv=5,
    scoring='f1',
    random_state=42,
    n_jobs=-1,
    verbose=2
)

# Entraînement
search.fit(X_train, y_train)
```

### Cross-Validation

```python
from sklearn.model_selection import cross_val_score

cv_scores = cross_val_score(
    pipeline,
    X_train,
    y_train,
    cv=5,
    scoring='f1'
)
print(f"F1 CV: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
```

---

## 📊 MLflow Tracking

### Configuration

```python
import mlflow

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("Employee_Turnover_Training")
```

### Logging

```python
with mlflow.start_run():
    # Paramètres
    mlflow.log_params(best_params)
    
    # Métriques
    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("roc_auc", roc_auc)
    
    # Artifacts
    mlflow.log_artifact("model.pkl")
    mlflow.log_artifact("scaler.joblib")
    mlflow.log_artifact("onehot_encoder.joblib")
    mlflow.log_artifact("ordinal_encoder.joblib")
    
    # Modèle
    mlflow.sklearn.log_model(model, "model")
```

### Visualiser les Résultats

```bash
# Démarrer l'UI MLflow
mlflow ui --backend-store-uri sqlite:///mlflow.db

# Ouvrir http://localhost:5000
```

**Interface MLflow** :
- Liste des runs avec métriques
- Comparaison de paramètres
- Visualisation des artifacts
- Téléchargement des modèles

---

## 📦 Artifacts Sauvegardés

| Fichier | Description | Utilisation |
|---------|-------------|-------------|
| `model.pkl` | Modèle XGBoost entraîné | Prédictions API |
| `scaler.joblib` | StandardScaler fitté | Preprocessing API |
| `onehot_encoder.joblib` | OneHotEncoder fitté | Encoding API |
| `ordinal_encoder.joblib` | OrdinalEncoder fitté | Encoding API |

---

## 🚀 Déployer le Nouveau Modèle

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

### 2. L'API Charge Automatiquement

Au redémarrage, l'API télécharge le modèle depuis HuggingFace Hub.

```python
# Dans src/models.py
from huggingface_hub import hf_hub_download

model_path = hf_hub_download(
    repo_id="ASI-Engineer/employee-turnover-model",
    filename="model/model.pkl"
)
model = joblib.load(model_path)
```

---

## 📈 Résultats Actuels

| Métrique | Valeur | CV (5-fold) |
|----------|--------|-------------|
| **F1 Score** | 0.85 | 0.85 ± 0.03 |
| **Precision** | 0.82 | 0.82 ± 0.04 |
| **Recall** | 0.88 | 0.88 ± 0.03 |
| **ROC AUC** | 0.91 | 0.91 ± 0.02 |

---

## 🔄 Workflow de Ré-entraînement

### 1. Ajouter Nouvelles Données

```bash
# Placer les nouveaux CSV dans data/
cp new_sondage.csv data/extrait_sondage.csv
cp new_eval.csv data/extrait_eval.csv
cp new_sirh.csv data/extrait_sirh.csv
```

### 2. Ré-entraîner

```bash
poetry run python ml_model/main.py
```

### 3. Comparer dans MLflow

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

**Vérifier** :
- F1 Score : amélioration ?
- Recall : maintenu > 0.85 ?
- ROC AUC : maintenu > 0.90 ?

### 4. Valider sur Test Set

```python
from sklearn.metrics import classification_report

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
```

### 5. Déployer si Meilleur

```bash
# Uploader sur HuggingFace
poetry run python -c "
from huggingface_hub import HfApi
api = HfApi()
api.upload_file(
    path_or_fileobj='model.pkl',
    path_in_repo='model/model.pkl',
    repo_id='ASI-Engineer/employee-turnover-model'
)
"

# Redémarrer l'API
# Le nouveau modèle sera chargé automatiquement
```

---

## 🔧 Optimisation Avancée

### Tuning Manuel

Modifier `ml_model/train_model.py` :

```python
# Augmenter les itérations RandomizedSearchCV
n_iter=2000  # au lieu de 1000

# Ajuster la plage des hyperparamètres
'xgb__max_depth': [5, 7, 10, 12, 15, 20],
'xgb__learning_rate': [0.005, 0.01, 0.05, 0.1, 0.15],
```

### Features Supplémentaires

Ajouter dans `ml_model/preprocess.py` :

```python
# Exemples d'idées
df['taux_augmentation'] = df['augementation_salaire'] / df['revenu']
df['ecart_evaluations'] = df['note_actuelle'] - df['note_precedente']
df['ratio_formations_anciennete'] = df['nb_formations'] / (df['anciennete'] + 1)
```

---

## 🔗 Liens Utiles

- [Modèle ML](model.md)
- [API](api.md)
- [Déploiement](deployment.md)
