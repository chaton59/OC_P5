
# 🚀 API Employee Turnover Prediction (v3.2.1)

API REST FastAPI pour prédire le risque de départ d'un employé.

## 📋 Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/docs` | Documentation Swagger |
| GET | `/ui` | Interface Gradio |
| POST | `/predict` | Prédiction unitaire (JSON, contraintes réelles) |
| POST | `/predict/batch` | Prédiction batch (3 fichiers CSV bruts) |

## 🚀 Démarrage rapide

```bash
# Installation
poetry install

# Lancement (dev)
poetry run uvicorn app:app --reload

# Lancement (prod)
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2
```

**URLs disponibles :**
- API : http://localhost:8000
- Swagger : http://localhost:8000/docs
- Interface Gradio : http://localhost:8000/ui

## 🔐 Authentification

Les endpoints `/predict` et `/predict/batch` sont protégés par API Key en production (`DEBUG=False`).

### Configuration
```bash
# .env
API_KEY=votre-cle-secrete
DEBUG=False  # Active l'authentification
```

### Utilisation
```bash
curl -X POST http://localhost:8000/predict \
  -H "X-API-Key: votre-cle-secrete" \
  -H "Content-Type: application/json" \
  -d @employee.json
```

### Générer une clé
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📊 Prédiction unitaire (POST /predict)

### Données d'entrée (format JSON)


**Contraintes de validation strictes** (v3.2.1, issues des données d'entraînement) :

| Champ | Type | Plage | Description |
|-------|------|-------|-------------|
| `nombre_participation_pee` | int | 0-3 | Participations au PEE |
| `nb_formations_suivies` | int | 0-6 | Formations suivies |
| `nombre_employee_sous_responsabilite` | int | 1 (fixe) | Employés sous responsabilité |
| `distance_domicile_travail` | int | 1-30 | Distance en km |
| `niveau_education` | int | 1-5 | Niveau d'éducation |
| `domaine_etude` | enum | Infra & Cloud, Transformation Digitale, Marketing, Entrepreunariat, Ressources Humaines, Autre | Domaine d'études |
| `ayant_enfants` | "Y"/"N" | | A des enfants |
| `frequence_deplacement` | enum | Aucun, Occasionnel, Frequent | Fréquence déplacements |
| `annees_depuis_la_derniere_promotion` | int | 0-15 | Années depuis promotion |
| `annes_sous_responsable_actuel` | int | 0-17 | Années sous responsable |
| `satisfaction_employee_environnement` | int | 1-4 | Satisfaction environnement |
| `note_evaluation_precedente` | int | 1-4 | Note évaluation précédente |
| `niveau_hierarchique_poste` | int | 1-5 | Niveau hiérarchique |
| `satisfaction_employee_nature_travail` | int | 1-4 | Satisfaction nature travail |
| `satisfaction_employee_equipe` | int | 1-4 | Satisfaction équipe |
| `satisfaction_employee_equilibre_pro_perso` | int | 1-4 | Équilibre pro/perso |
| `note_evaluation_actuelle` | int | 3-4 | Note évaluation actuelle |
| `heure_supplementaires` | "Oui"/"Non" | | Heures supplémentaires |
| `augementation_salaire_precedente` | float | 0-100 | Augmentation (%) |
| `age` | int | 18-60 | Âge |
| `genre` | "M"/"F" | | Genre |
| `revenu_mensuel` | float | 1000-20000 | Revenu mensuel (€) |
| `statut_marital` | enum | Célibataire, Marié(e), Divorcé(e) | Statut marital |
| `departement` | enum | Commercial, Consulting, Ressources Humaines | Département |
| `poste` | enum | Cadre Commercial, Assistant de Direction, Consultant, Tech Lead, Manager, Senior Manager, Représentant Commercial, Directeur Technique, Ressources Humaines | Poste |
| `nombre_experiences_precedentes` | int | 0-9 | Expériences précédentes |
| `nombre_heures_travailless` | int | 80 (fixe) | Heures/semaine |
| `annee_experience_totale` | int | 0-40 | Années expérience totale |
| `annees_dans_l_entreprise` | int | 0-40 | Années dans l'entreprise |
| `annees_dans_le_poste_actuel` | int | 0-18 | Années dans le poste |


**Remarque :** Toute valeur hors de ces bornes ou listes sera rejetée (422).

```json
{
  "nombre_participation_pee": 0,
  "nb_formations_suivies": 2,
  "nombre_employee_sous_responsabilite": 1,
  "distance_domicile_travail": 15,
  "niveau_education": 3,
  "domaine_etude": "Infra & Cloud",
  "ayant_enfants": "Y",
  "frequence_deplacement": "Occasionnel",
  "annees_depuis_la_derniere_promotion": 2,
  "annes_sous_responsable_actuel": 5,
  "satisfaction_employee_environnement": 3,
  "note_evaluation_precedente": 4,
  "niveau_hierarchique_poste": 2,
  "satisfaction_employee_nature_travail": 3,
  "satisfaction_employee_equipe": 3,
  "satisfaction_employee_equilibre_pro_perso": 2,
  "note_evaluation_actuelle": 4,
  "heure_supplementaires": "Non",
  "augementation_salaire_precedente": 5.5,
  "age": 35,
  "genre": "M",
  "revenu_mensuel": 4500.0,
  "statut_marital": "Marié(e)",
  "departement": "Commercial",
  "poste": "Manager",
  "nombre_experiences_precedentes": 3,
  "nombre_heures_travailless": 80,
  "annee_experience_totale": 10,
  "annees_dans_l_entreprise": 5,
  "annees_dans_le_poste_actuel": 2
}
```


### Réponse
```json
{
  "prediction": 0,
  "probability_0": 0.85,
  "probability_1": 0.15,
  "risk_level": "Low"
}
```

## 📦 Prédiction batch (POST /predict/batch)

**Nouveau !** Envoyez directement les 3 fichiers CSV bruts pour obtenir les prédictions de tous les employés.

### Requête
```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "X-API-Key: votre-cle-secrete" \
  -F "sondage_file=@data/extrait_sondage.csv" \
  -F "eval_file=@data/extrait_eval.csv" \
  -F "sirh_file=@data/extrait_sirh.csv"
```


### Fichiers attendus

| Fichier | Description | Colonnes clés |
|---------|-------------|---------------|
| `sondage_file` | Données sondage satisfaction | `code_sondage`, `satisfaction_*`, `frequence_deplacement`, ... |
| `eval_file` | Données évaluations | `eval_number`, `note_evaluation_*`, `heure_supplementaires`, ... |
| `sirh_file` | Données RH administratives | `id_employee`, `age`, `genre`, `revenu_mensuel`, `poste`, ... |

### Réponse
```json
{
  "total_employees": 1470,
  "predictions": [
    {
      "employee_id": 1,
      "prediction": 1,
      "probability_stay": 0.16,
      "probability_leave": 0.84,
      "risk_level": "High"
    },
    {
      "employee_id": 2,
      "prediction": 0,
      "probability_stay": 0.89,
      "probability_leave": 0.11,
      "risk_level": "Low"
    }
  ],
  "summary": {
    "total_stay": 1169,
    "total_leave": 301,
    "high_risk_count": 222,
    "medium_risk_count": 233,
    "low_risk_count": 1015
  }
}
```

### Exemple Python
```python
import requests

url = "http://localhost:8000/predict/batch"
headers = {"X-API-Key": "votre-cle-secrete"}

files = {
    "sondage_file": open("data/extrait_sondage.csv", "rb"),
    "eval_file": open("data/extrait_eval.csv", "rb"),
    "sirh_file": open("data/extrait_sirh.csv", "rb"),
}

response = requests.post(url, headers=headers, files=files)
data = response.json()

print(f"Total employés: {data['total_employees']}")
print(f"À risque élevé: {data['summary']['high_risk_count']}")

# Filtrer les employés à haut risque
high_risk = [p for p in data["predictions"] if p["risk_level"] == "High"]
for emp in high_risk[:5]:
    print(f"  ID {emp['employee_id']}: {emp['probability_leave']:.1%} de départ")
```


## 🔄 Preprocessing

Le preprocessing est appliqué automatiquement à chaque requête :

1. **Feature Engineering** : ratios (revenu/ancienneté), moyennes satisfaction
2. **Encoding** : OneHot (genre, département, poste...), Ordinal (fréquence déplacement)
3. **Scaling** : StandardScaler sur variables numériques (min/max réels appliqués)

## ⚠️ Codes d'erreur

| Code | Description |
|------|-------------|
| 200 | Succès |
| 401 | API Key manquante ou invalide |
| 422 | Données invalides (validation Pydantic) |
| 429 | Rate limit dépassé (20 req/min) |
| 500 | Erreur serveur |

## 🧪 Tests

```bash
# Lancer tous les tests
poetry run pytest

# Avec couverture
poetry run pytest --cov=src --cov=app

# Tests spécifiques
poetry run pytest tests/test_api_predict.py -v
```


## 📁 Structure du code

```
src/
├── auth.py          # Authentification API Key
├── config.py        # Configuration (.env)
├── gradio_ui.py     # Interface Gradio (sliders = min/max réels)
├── logger.py        # Logging JSON structuré
├── models.py        # Chargement modèle HF Hub
├── preprocessing.py # Pipeline de transformation (scaling, encoding)
├── rate_limit.py    # Rate limiting SlowAPI
└── schemas.py       # Schémas Pydantic (validation stricte)
```
