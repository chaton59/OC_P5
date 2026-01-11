# 🤖 Modèle Machine Learning

Documentation technique du modèle Employee Turnover Prediction.

---

## 📊 Vue d'Ensemble

**Algorithme** : XGBoost avec SMOTE  
**Type** : Classification binaire (départ / reste)  
**Dataset** : 1470 employés, 29 variables  
**Performance** : F1 Score 0.85, Recall 88%

---

## 🏗️ Architecture

### Pipeline Complet

```
DONNÉES BRUTES (3 CSV)
├── extrait_sondage.csv
├── extrait_eval.csv
└── extrait_sirh.csv
    │
    ▼
PREPROCESSING
├── Fusion sur employee_id
├── Nettoyage (duplicatas, outliers)
├── Feature Engineering (ratios, moyennes)
├── Encoding (OneHot + Ordinal)
└── Scaling (StandardScaler)
    │
    ▼
RÉÉQUILIBRAGE (SMOTE)
├── 79% reste → 50% reste
└── 21% part → 50% part
    │
    ▼
MODÈLE XGBOOST
├── RandomizedSearchCV (1000 itérations)
├── Cross-validation 5-fold
└── Optimisation F1 Score
    │
    ▼
PRÉDICTIONS
├── Classe: 0 (reste) / 1 (part)
├── Probabilités: [0.0 - 1.0]
└── Niveau de risque: Low/Medium/High
```

---

## 🔧 Preprocessing

### 1. Fusion des Données

Merge des 3 sources sur `employee_id` :
- `extrait_sondage.csv` : satisfaction, formations
- `extrait_eval.csv` : évaluations, promotions
- `extrait_sirh.csv` : données administratives

### 2. Nettoyage

- **Duplicatas** : suppression
- **Outliers** : winsorization (1% chaque côté)
- **Parsing** : `"11 %"` → `11.0`

### 3. Feature Engineering

| Feature Créée | Formule | Objectif |
|---------------|---------|----------|
| `revenu_par_anciennete` | revenu / (ancienneté + 1) | Détecter sous-rémunération |
| `experience_par_anciennete` | exp_totale / (ancienneté + 1) | Identifier surqualifiés |
| `satisfaction_moyenne` | mean(4 satisfactions) | Agrégat de satisfaction |
| `promo_par_anciennete` | années_promo / (ancienneté + 1) | Détecter stagnation |

**Impact** : +7% F1 Score

### 4. Encoding

**OneHot** (variables non-ordonnées) :
- `genre` : Homme / Femme
- `statut_marital` : Marié / Célibataire / Divorcé
- `departement` : Commercial, RH, Recherche, IT, Ventes
- `poste` : 15 postes différents
- `domaine_etude` : 6 domaines

**Ordinal** (variable ordonnée) :
- `frequence_deplacement` : Aucun (0) < Occasionnel (1) < Frequent (2)

### 5. Scaling

**StandardScaler** sur toutes les features numériques :
- Moyenne = 0
- Écart-type = 1

---

## ⚖️ Rééquilibrage SMOTE

**Problème** : Dataset déséquilibré (79% reste / 21% part)  
**Solution** : SMOTE (Synthetic Minority Over-sampling Technique)

### Principe

Crée des exemples synthétiques de la classe minoritaire par interpolation k-NN.

### Application

- **Avant SMOTE** : 1176 reste (79%) / 294 part (21%)
- **Après SMOTE** : 1176 reste (50%) / 1176 part (50%)
- **Appliqué** : Training set uniquement (CV-safe)

### Alternatives Écartées

| Technique | Problème |
|-----------|----------|
| Random Over-sampling | Surapprentissage (duplication exacte) |
| Random Under-sampling | Perte d'information |
| Class weights | -8% F1 vs SMOTE |

---

## 🎯 Modèle XGBoost

### Hyperparamètres Optimisés

RandomizedSearchCV avec 1000 itérations, 5-fold CV :

| Paramètre | Plage | Optimal | Rôle |
|-----------|-------|---------|------|
| `n_estimators` | 100-1000 | 300 | Nombre d'arbres |
| `max_depth` | 3-15 | 7 | Profondeur des arbres |
| `learning_rate` | 0.001-0.5 | 0.1 | Taux d'apprentissage |
| `subsample` | 0.4-1.0 | 0.8 | Échantillonnage données |
| `colsample_bytree` | 0.5-1.0 | 0.9 | Échantillonnage features |
| `reg_alpha` | 0-3 | 0.5 | Régularisation L1 |
| `gamma` | 0-10 | 2 | Seuil de split |

### Pourquoi XGBoost ?

| Algorithme | F1 Score | Avantage XGBoost |
|------------|----------|------------------|
| Logistic Regression | 0.65 | Capture relations non-linéaires |
| Random Forest | 0.78 | +7% performance |
| **XGBoost** | **0.85** | Régularisation + Boosting |
| Neural Network | N/A | Dataset trop petit |

---

## 📈 Performances

### Métriques Globales

| Métrique | Valeur | Interprétation |
|----------|--------|----------------|
| **F1 Score** | 0.85 | Excellent équilibre précision/recall |
| **Precision** | 0.82 | 82% des "départs" prédits sont corrects |
| **Recall** | 0.88 | 88% des vrais départs sont détectés |
| **ROC AUC** | 0.91 | Excellente capacité de discrimination |
| **Accuracy** | 0.85 | 85% de prédictions correctes |

### Matrice de Confusion

```
                Prédiction
            Reste     Part
Réalité
Reste       220       30        (88% spécificité)
Part         36      264        (88% recall)
```

**Analyse** :
- **Faux positifs** (30) : Employés fidèles identifiés à risque → Attention inutile
- **Faux négatifs** (36) : Départs non détectés → Perte de talents
- **Trade-off** : Privilégie recall (ne pas rater de départs)

### Validation Croisée

- **Méthode** : 5-fold stratified
- **F1 moyen** : 0.85 ± 0.03
- **Variance** : Faible → modèle robuste

---

## 🎯 Features Importantes

Top 10 des variables les plus prédictives :

| Rang | Feature | Impact | Explication |
|------|---------|--------|-------------|
| 1 | `satisfaction_employee_equilibre_pro_perso` | +++++ | Équilibre vie pro/perso critique |
| 2 | `annees_dans_l_entreprise` | ++++ | Juniors et très seniors à risque |
| 3 | `heure_supplementaires` | ++++ | Heures sup → burnout |
| 4 | `revenu_mensuel` | +++ | Bas salaires → départ |
| 5 | `satisfaction_moyenne` | +++ | Agrégat de satisfaction |
| 6 | `age` | +++ | Jeunes et seniors mobiles |
| 7 | `distance_domicile_travail` | ++ | Distance élevée → insatisfaction |
| 8 | `nb_formations_suivies` | ++ | Peu de formations → stagnation |
| 9 | `note_evaluation_actuelle` | ++ | Mauvaises évaluations → départ |
| 10 | `revenu_par_anciennete` | ++ | Sous-rémunération détectée |

---

## 🔄 Maintenance

### Quand Ré-entraîner ?

| Scénario | Fréquence | Déclencheur |
|----------|-----------|-------------|
| **Nouveaux données** | Trimestriel | +500 nouvelles entrées |
| **Drift détecté** | Immédiat | Performance < 0.75 F1 |
| **Changements métier** | Ponctuel | Nouvelles variables RH |

### Protocole de Ré-entraînement

1. Ajouter nouvelles données dans `data/`
2. Lancer `python ml_model/main.py`
3. Comparer dans MLflow : F1, Precision, Recall
4. Valider sur test set
5. Si F1 > ancien modèle → uploader sur HuggingFace

```bash
# Ré-entraîner
poetry run python ml_model/main.py

# Comparer dans MLflow
mlflow ui --backend-store-uri sqlite:///mlflow.db

# Uploader nouveau modèle
poetry run python -c "
from huggingface_hub import HfApi
api = HfApi()
api.upload_file(
    path_or_fileobj='model.pkl',
    path_in_repo='model/model.pkl',
    repo_id='ASI-Engineer/employee-turnover-model'
)
"
```

### Monitoring en Production

**Métriques à surveiller** :
- Distribution des prédictions (% Oui/Non)
- Probabilités moyennes
- Taux de requêtes 422 (validation failed)

**Alerte si** :
- Prédictions "Oui" > 40% (vs 21% attendu)
- Probabilités moyennes < 0.3 ou > 0.7
- Taux d'erreurs 422 > 5%

---

## 📊 Dataset

| Caractéristique | Valeur |
|-----------------|--------|
| **Taille totale** | 1470 employés |
| **Features brutes** | 29 colonnes |
| **Features après encoding** | 45 (après OneHot) |
| **Classe cible** | `a_quitte_l_entreprise` (Oui/Non) |
| **Déséquilibre initial** | 79% Reste / 21% Part |
| **Déséquilibre après SMOTE** | 50% / 50% (train uniquement) |
| **Split** | 80% train / 20% test (stratifié) |

---

## 🔗 Liens Utiles

- [Entraînement](training.md)
- [API](api.md)
- [Installation](installation.md)
