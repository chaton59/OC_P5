# 📚 Documentation API

Documentation complète des endpoints de l'API Employee Turnover Prediction.

## Base URL

- **Local** : `http://localhost:8000`
- **Production** : `https://asi-engineer-oc-p5.hf.space`
- **Documentation interactive** : `/docs` (Swagger) | `/redoc` (ReDoc)

## 🔐 Authentification

L'API utilise une **API Key** via le header `X-API-Key`.

| Environnement | Auth requise | Rate limit |
|---------------|--------------|------------|
| **Dev** (DEBUG=true) | ❌ Non | ❌ Désactivé |
| **Prod** (DEBUG=false) | ✅ Oui | ✅ 20 req/min |

### Exemple d'utilisation

```bash
# Production
curl -H "X-API-Key: your-secret-key" \
     https://asi-engineer-oc-p5.hf.space/health

# Développement
curl http://localhost:8000/health
```

**Erreur 401** : `{"detail": "Missing API Key"}`

---

## Endpoints

### 1. GET /health

Vérifie l'état de l'API et du modèle.

**Réponse 200**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_type": "Pipeline",
  "version": "3.3.0"
}
```

**Exemple**
```bash
curl http://localhost:8000/health
```

---

### 2. POST /predict

Prédit le risque de départ d'un employé.

**Headers**
```
Content-Type: application/json
X-API-Key: your-key  # Prod uniquement
```

**Corps de la requête**
```json
{
  "age": 35,
  "genre": "Homme",
  "revenu_mensuel": 4500,
  "departement": "Commercial",
  "poste": "Conseiller Clientèle",
  "statut_marital": "Célibataire",
  "annees_dans_l_entreprise": 3,
  "annee_experience_totale": 8,
  "distance_domicile_travail": 15,
  "niveau_education": "Licence",
  "domaine_etude": "Commerce",
  "ayant_enfants": "Non",
  "frequence_deplacement": "Occasionnel",
  "heure_supplementaires": "Oui",
  "nombre_participation_pee": 2,
  "nb_formations_suivies": 3,
  "satisfaction_employee_environnement": 3,
  "satisfaction_employee_nature_travail": 4,
  "satisfaction_employee_equilibre_pro_perso": 2,
  "satisfaction_employee_relation_hierarchique": 3,
  "augementation_salaire_precedente": 12,
  "note_evaluation_actuelle": 3,
  "note_evaluation_precedente": 3,
  "annee_derniere_promotion": 0,
  "nombre_annee_avec_manager": 2,
  "nombre_boite_travaille_avant": 1
}
```

**Validation des champs critiques**

| Champ | Type | Contraintes |
|-------|------|-------------|
| `age` | int | 18-100 |
| `revenu_mensuel` | int | > 0 |
| `genre` | str | "Homme" ou "Femme" |
| `departement` | str | Commercial, RH, Recherche, IT, Ventes |
| `satisfaction_*` | int | 1-4 |
| `frequence_deplacement` | str | "Aucun", "Occasionnel", "Frequent" |

**Réponse 200**
```json
{
  "employee_id": null,
  "prediction": "Oui",
  "probability": 0.7823,
  "risk_level": "High",
  "model_version": "3.3.0",
  "timestamp": "2026-01-11T17:30:45.123456"
}
```

**Niveaux de risque**

| risk_level | Probabilité | Interprétation |
|------------|-------------|----------------|
| Low | < 0.3 | Employé stable |
| Medium | 0.3 - 0.7 | Risque modéré |
| High | > 0.7 | Risque élevé de départ |

**Erreur 422 : Validation échouée**
```json
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "ensure this value is greater than or equal to 18",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

**Exemple Python**
```python
import requests

url = "http://localhost:8000/predict"
headers = {"Content-Type": "application/json"}
data = {
    "age": 35,
    "genre": "Homme",
    "revenu_mensuel": 4500,
    "departement": "Commercial",
    # ... autres champs
}

response = requests.post(url, json=data, headers=headers)
result = response.json()
print(f"Prédiction: {result['prediction']} "
      f"(probabilité: {result['probability']:.2%})")
```

---

### 3. POST /predict/batch

Traite plusieurs employés depuis 3 fichiers CSV.

**Headers**
```
Content-Type: multipart/form-data
X-API-Key: your-key  # Prod uniquement
```

**Fichiers requis**

| Paramètre | Fichier | Description |
|-----------|---------|-------------|
| `sondage_file` | CSV | Données sondage satisfaction |
| `eval_file` | CSV | Données évaluation performance |
| `sirh_file` | CSV | Données RH administratives |

**Exemple curl**
```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "X-API-Key: your-key" \
  -F "sondage_file=@data/extrait_sondage.csv" \
  -F "eval_file=@data/extrait_eval.csv" \
  -F "sirh_file=@data/extrait_sirh.csv"
```

**Réponse 200**
```json
{
  "total_employees": 1470,
  "predictions": [
    {
      "employee_id": "EMP001",
      "prediction": "Non",
      "probability": 0.23,
      "risk_level": "Low"
    },
    {
      "employee_id": "EMP002",
      "prediction": "Oui",
      "probability": 0.89,
      "risk_level": "High"
    }
  ],
  "summary": {
    "will_leave": 294,
    "will_stay": 1176,
    "high_risk": 147,
    "medium_risk": 441,
    "low_risk": 882
  },
  "timestamp": "2026-01-11T17:35:22.456789"
}
```

**Exemple Python**
```python
import requests

url = "http://localhost:8000/predict/batch"
files = {
    'sondage_file': open('data/extrait_sondage.csv', 'rb'),
    'eval_file': open('data/extrait_eval.csv', 'rb'),
    'sirh_file': open('data/extrait_sirh.csv', 'rb')
}

response = requests.post(url, files=files)
result = response.json()
print(f"Total: {result['total_employees']} employés")
print(f"Risque élevé: {result['summary']['high_risk']}")
```

---

## Export Swagger

Pour exporter la documentation Swagger en JSON :

```bash
curl http://localhost:8000/openapi.json > openapi.json
```

## Codes de Statut HTTP

| Code | Signification |
|------|---------------|
| 200 | Succès |
| 401 | Authentification échouée |
| 422 | Validation des données échouée |
| 429 | Limite de requêtes dépassée (rate limit) |
| 500 | Erreur serveur interne |

## Limites et Quotas

- **Rate limit** : 20 requêtes/minute (production)
- **Taille max fichier CSV** : 10 MB
- **Timeout** : 30 secondes par requête
