# 📚 API Guide

Documentation complète de l'API Employee Turnover Prediction.

---

## 🌟 Vue d'Ensemble

**Base URL** :  
- Local : `http://localhost:8000`  
- Production : `https://asi-engineer-oc-p5.hf.space`

**Documentation interactive** : `/docs` (Swagger) | `/redoc` (ReDoc)

---

## 🔐 Authentification

L'API utilise une **API Key** via le header HTTP `X-API-Key`.

### Configuration par Environnement

| Environnement | DEBUG | Auth requise | Rate limiting |
|---------------|-------|--------------|---------------|
| **Dev** | `true` | ❌ Non | ❌ Désactivé |
| **Prod** | `false` | ✅ Oui | ✅ 20 req/min |

### Utilisation

```bash
# Production (avec authentification)
curl -X POST https://asi-engineer-oc-p5.hf.space/predict \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d @employee_data.json

# Développement (sans authentification)
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @employee_data.json
```

### Erreur 401 : Missing API Key

```json
{"detail": "Missing API Key"}
```

---

## 📡 Endpoints

### 1. Health Check

Vérifie l'état de l'API et du modèle.

```http
GET /health
```

#### Réponse 200 OK

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_type": "Pipeline",
  "version": "3.3.0"
}
```

#### Exemple curl

```bash
curl http://localhost:8000/health
```

---

### 2. Prédiction Unitaire

Prédit le risque de départ d'un employé.

```http
POST /predict
```

#### Headers

```http
Content-Type: application/json
X-API-Key: your-key  # Requis en production
```

#### Corps de la Requête

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

#### Validation des Champs

| Champ | Type | Contraintes |
|-------|------|-------------|
| `age` | int | 18-100 |
| `revenu_mensuel` | int | > 0 |
| `genre` | str | "Homme", "Femme" |
| `departement` | str | Commercial, RH, Recherche, IT, Ventes |
| `satisfaction_*` | int | 1-4 |
| `frequence_deplacement` | str | "Aucun", "Occasionnel", "Frequent" |

#### Réponse 200 OK

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

#### Niveaux de Risque

| risk_level | Probabilité | Interprétation |
|------------|-------------|----------------|
| **Low** | < 0.3 | Employé stable |
| **Medium** | 0.3 - 0.7 | Risque modéré |
| **High** | > 0.7 | Risque élevé de départ |

#### Erreur 422 : Validation Failed

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

---

### 3. Prédiction Batch

Traite plusieurs employés depuis 3 fichiers CSV.

```http
POST /predict/batch
```

#### Headers

```http
Content-Type: multipart/form-data
X-API-Key: your-key  # Requis en production
```

#### Fichiers Requis

| Fichier | Description |
|---------|-------------|
| `sondage_file` | Données sondage satisfaction |
| `eval_file` | Données évaluation performance |
| `sirh_file` | Données RH administratives |

#### Exemple curl

```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "X-API-Key: your-key" \
  -F "sondage_file=@data/extrait_sondage.csv" \
  -F "eval_file=@data/extrait_eval.csv" \
  -F "sirh_file=@data/extrait_sirh.csv"
```

#### Réponse 200 OK

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

---

## 🐍 Exemples de Code

### Python avec requests

```python
import requests

url = "http://localhost:8000/predict"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "your-secret-key"  # En production
}
data = {
    "age": 35,
    "genre": "Homme",
    "revenu_mensuel": 4500,
    # ... autres champs
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print(f"Prédiction: {result['prediction']}")
print(f"Probabilité: {result['probability']:.2%}")
print(f"Niveau de risque: {result['risk_level']}")
```

### JavaScript avec fetch

```javascript
const url = 'http://localhost:8000/predict';
const data = {
  age: 35,
  genre: 'Homme',
  revenu_mensuel: 4500,
  // ... autres champs
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-secret-key'  // En production
  },
  body: JSON.stringify(data)
})
  .then(response => response.json())
  .then(result => {
    console.log('Prédiction:', result.prediction);
    console.log('Probabilité:', result.probability);
    console.log('Risque:', result.risk_level);
  });
```

### Bash avec curl

```bash
#!/bin/bash

# Prédiction unitaire
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
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
  }' | jq .
```

---

## ⚠️ Codes d'Erreur

| Code | Erreur | Cause | Solution |
|------|--------|-------|----------|
| **200** | OK | Succès | - |
| **401** | Unauthorized | API Key manquante/invalide | Ajouter header `X-API-Key` |
| **422** | Unprocessable Entity | Validation Pydantic échouée | Vérifier format des données |
| **429** | Too Many Requests | Rate limit dépassé (20/min) | Attendre avant nouvelle requête |
| **500** | Internal Server Error | Erreur serveur | Consulter les logs |
| **503** | Service Unavailable | Modèle non chargé | Vérifier health check |

---

## 🛡️ Rate Limiting

**Limite** : 20 requêtes par minute (par IP ou API Key)  
**Environnement** : Production uniquement (`DEBUG=false`)

### Headers de Réponse

```http
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 15
X-RateLimit-Reset: 1672531200
```

### Erreur 429

```json
{
  "error": "Rate limit exceeded",
  "message": "20 per 1 minute"
}
```

---

## 📊 Logging et Traçabilité

Toutes les prédictions sont enregistrées dans :

- **PostgreSQL** (table `ml_logs`) : traçabilité complète
- **Logs JSON** (`logs/api.log`) : monitoring structuré

### Format du Log JSON

```json
{
  "timestamp": "2026-01-11T17:40:12.345678",
  "level": "INFO",
  "message": "Prediction successful",
  "method": "POST",
  "path": "/predict",
  "status_code": 200,
  "duration_ms": 23.45,
  "prediction": "Oui",
  "probability": 0.78,
  "risk_level": "High"
}
```

---

## 🔗 Liens Utiles

- [Installation](installation.md)
- [Configuration](configuration.md)
- [Modèle ML](model.md)
- [Déploiement](deployment.md)
