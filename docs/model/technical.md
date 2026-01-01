# Documentation Technique du Modèle

!!! info "Documentation Source"
    Cette page est basée sur [MODEL_TECHNICAL.md](../../MODEL_TECHNICAL.md). 
    Consultez le fichier source pour la version la plus récente.

## Vue d'ensemble

Le modèle de prédiction du turnover utilise **XGBoost** (Extreme Gradient Boosting) avec **SMOTE** (Synthetic Minority Over-sampling Technique) pour gérer le déséquilibre de classes.

### Caractéristiques

- **Algorithme** : XGBoost Classifier
- **Dataset** : 1470 employés, 29 features
- **Déséquilibre initial** : 79.5% restent / 20.5% partent
- **Après SMOTE** : 50% / 50% (données synthétiques)
- **Performance** : F1=0.85, Precision=0.82, Recall=0.88, ROC AUC=0.91

---

## 🏗️ Architecture

### Pipeline de Prédiction

```
┌─────────────────┐
│  DONNÉES BRUTES │ (29 features RH)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      ÉTAPE 1 : PREPROCESSING        │
│  ┌──────────────────────────────┐   │
│  │ • Nettoyage valeurs manquantes│  │
│  │ • Encodage catégorielles      │  │
│  │   (Label/One-Hot)             │  │
│  │ • Scaling numériques          │  │
│  │   (StandardScaler)            │  │
│  └──────────────────────────────┘   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   ÉTAPE 2 : FEATURE ENGINEERING     │
│  ┌──────────────────────────────┐   │
│  │ • Ratios dérivés              │  │
│  │   (salaire/expérience)        │  │
│  │ • Interactions de features    │  │
│  │ • Binning (âge, ancienneté)   │  │
│  └──────────────────────────────┘   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    ÉTAPE 3 : SMOTE (Entraînement)   │
│  ┌──────────────────────────────┐   │
│  │ • Génération d'exemples       │  │
│  │   synthétiques minoritaires   │  │
│  │ • Équilibrage 50/50           │  │
│  │ • Évite l'overfitting         │  │
│  └──────────────────────────────┘   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     ÉTAPE 4 : MODÈLE XGBOOST        │
│  ┌──────────────────────────────┐   │
│  │ • Gradient Boosting Trees     │  │
│  │ • max_depth=6, n_estimators   │  │
│  │ • learning_rate=0.1           │  │
│  │ • RandomizedSearchCV          │  │
│  └──────────────────────────────┘   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      ÉTAPE 5 : OUTPUT               │
│  ┌──────────────────────────────┐   │
│  │ • Probabilités (classe 0/1)   │  │
│  │ • Prédiction binaire          │  │
│  │ • Niveau de risque            │  │
│  │   (Low/Medium/High)           │  │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 📊 Performances

### Métriques Principales

![Performances du Modèle](../../model_performance.png)

| Métrique | Score | Interprétation |
|----------|-------|----------------|
| **F1 Score** | 0.85 | Excellent équilibre précision/recall |
| **Precision** | 0.82 | 82% des "va partir" sont vrais |
| **Recall** | 0.88 | 88% des vrais départs détectés |
| **ROC AUC** | 0.91 | Excellente discrimination |

!!! success "Points forts"
    - **Recall élevé (88%)** : Détecte la majorité des employés à risque
    - **Faux positifs limités (18%)** : Évite les alertes excessives
    - **ROC AUC > 0.90** : Excellente capacité prédictive

### Matrice de Confusion (Test Set)

```
                 Prédiction
              Reste (0)  Part (1)
Réalité  
Reste (0)      220        30      (88% Spécificité)
Part (1)        36       264      (88% Recall)
```

**Analyse** :
- **Vrais Négatifs (220)** : Employés correctement identifiés comme restant
- **Vrais Positifs (264)** : Départs correctement prédits
- **Faux Positifs (30)** : Fausses alertes (12%)
- **Faux Négatifs (36)** : Départs manqués (12%)

---

## 🎯 Choix Techniques

### Pourquoi XGBoost ?

| Critère | XGBoost | Random Forest | Logistic Regression |
|---------|---------|---------------|---------------------|
| **F1 Score** | 0.85 ✅ | 0.78 | 0.65 |
| **Vitesse d'entraînement** | Rapide | Lente | Très rapide |
| **Interprétabilité** | Moyenne | Moyenne | Élevée |
| **Gestion non-linéarités** | ✅ Excellente | Bonne | ❌ Limitée |
| **Overfitting** | ✅ Régularisation L1/L2 | Risque moyen | Faible |

!!! tip "Verdict"
    XGBoost offre **+7% de F1** par rapport à Random Forest et **+20%** par rapport à Logistic Regression, avec une vitesse d'entraînement acceptable (~2 minutes).

### Pourquoi SMOTE ?

| Critère | SMOTE | Class Weights | Undersampling | Aucun |
|---------|-------|---------------|---------------|-------|
| **F1 Score** | 0.85 ✅ | 0.78 | 0.72 | 0.68 |
| **Recall** | 0.88 ✅ | 0.81 | 0.79 | 0.65 |
| **Perte d'info** | ❌ Aucune | ❌ Aucune | ✅ Données supprimées | N/A |
| **Généralisation** | ✅ Bonne | Moyenne | Risquée | ❌ Mauvaise |

!!! tip "Verdict"
    SMOTE génère des exemples synthétiques intelligents (interpolation K-NN) sans perdre de données, offrant **+7% de F1** par rapport aux class weights.

---

## 🔧 Maintenance

### Protocole de Réentraînement

!!! warning "Fréquence Recommandée"
    **Tous les 3 mois** ou en cas de drift détecté (voir ci-dessous).

#### Étapes

1. **Collecter nouvelles données** (dernier trimestre)
2. **Fusionner avec dataset d'entraînement** (historique glissant 2 ans)
3. **Vérifier qualité** (valeurs manquantes, outliers)
4. **Réentraîner modèle** (`poetry run python ml_model/train_model.py`)
5. **Valider performances** (F1 > 0.83 requis)
6. **Déployer nouvelle version** (git tag + push)

### Détection de Drift

**Script** : `scripts/detect_drift.py`

```python
import pandas as pd
from scipy.stats import ks_2samp

# Charger données historiques et nouvelles
train_data = pd.read_csv("data/historical_dataset.csv")
new_data = pd.read_csv("data/new_quarter_data.csv")

# Test Kolmogorov-Smirnov pour chaque feature numérique
for col in train_data.select_dtypes(include=['float64', 'int64']).columns:
    stat, p_value = ks_2samp(train_data[col], new_data[col])
    if p_value < 0.05:
        print(f"⚠️  DRIFT détecté sur {col} (p={p_value:.4f})")
```

**Seuils d'alerte** :
- p-value < 0.05 : Drift significatif → Enquête recommandée
- p-value < 0.01 : Drift critique → Réentraînement urgent

---

## 📁 Fichiers Importants

| Fichier | Rôle |
|---------|------|
| `ml_model/train_model.py` | Script d'entraînement |
| `ml_model/preprocess.py` | Pipeline de preprocessing |
| `src/preprocessing.py` | Preprocessing pour inférence API |
| `src/models.py` | Chargement modèle depuis HF Hub |
| `docs/TRAINING.md` | Guide d'entraînement complet |

---

## 🔗 Liens Utiles

- **[Guide d'entraînement](training.md)** : Procédure complète
- **[Performances détaillées](performance.md)** : Analyse approfondie
- **[Architecture complète](architecture.md)** : Diagrammes détaillés
- **[MODEL_TECHNICAL.md](../../MODEL_TECHNICAL.md)** : Documentation source
