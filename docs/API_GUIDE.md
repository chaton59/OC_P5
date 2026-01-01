# 📚 Guide Complet de l'API Employee Turnover Prediction

**Version** : 3.2.1  
**Base URL** : `http://localhost:8000` (local) ou `https://asi-engineer-oc-p5.hf.space` (production)  
**Documentation interactive** : `/docs` (Swagger UI) | `/redoc` (ReDoc)

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Authentification](#authentification)
3. [Rate Limiting](#rate-limiting)
4. [Endpoints](#endpoints)
5. [Schémas Pydantic](#schémas-pydantic)
6. [Exemples d'utilisation](#exemples-dutilisation)
7. [Codes d'erreur](#codes-derreur)
8. [Bonnes pratiques](#bonnes-pratiques)

---

## 🌟 Vue d'ensemble

L'API Employee Turnover Prediction est une API REST construite avec **FastAPI** qui expose un modèle de Machine Learning pour prédire le risque de départ d'un employé.

### Caractéristiques principales

- ✅ **Validation stricte** : Pydantic pour valider automatiquement les données d'entrée
- ✅ **Documentation auto** : Swagger UI et ReDoc générés automatiquement par FastAPI
- ✅ **Sécurité** : Authentification par API Key en production
- ✅ **Performance** : Rate limiting pour éviter les abus
- ✅ **Monitoring** : Logs structurés JSON et endpoint de health check
- ✅ **Batch processing** : Traitement de fichiers CSV complets

### Technologies utilisées

| Technologie | Raison du choix |
|-------------|-----------------|
| **FastAPI** | Framework moderne, async, documentation auto, performance élevée |
| **Pydantic** | Validation robuste des données avec messages d'erreur clairs |
| **XGBoost** | Algorithme de boosting performant pour classification |
| **SMOTE** | Rééquilibrage des classes pour données déséquilibrées |
| **SlowAPI** | Rate limiting simple et efficace |
| **python-json-logger** | Logs structurés pour monitoring production |

---

## 🔐 Authentification

L'API utilise une **authentification par API Key** via le header HTTP `X-API-Key`.

### Configuration par environnement

| Environnement | DEBUG | Authentification requise | Rate limiting |
|---------------|-------|-------------------------|---------------|
| **Développement** | `true` | ❌ Non | ❌ Désactivé |
| **Production** | `false` | ✅ Oui | ✅ Activé |

### Configuration (.env)

```bash
# Mode développement (désactive auth)
DEBUG=true

# Mode production (active auth)
DEBUG=false
API_KEY=your-secret-api-key-here
```

### Génération d'une API Key sécurisée

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Résultat (exemple)
# XqR8kL3mN9pT2vW5yZ7aB4cD6eF8gH0iJ
```

### Utilisation de l'API Key

```bash
# Avec authentification (production)
curl -X POST http://localhost:8000/predict \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"age": 35, ...}'

# Sans authentification (développement, DEBUG=true)
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 35, ...}'
```

### Réponse en cas d'erreur d'authentification

```json
{
  "detail": "Missing API Key"
}
```

**Status code** : `401 Unauthorized`

---

## 🛡️ Rate Limiting

Pour éviter les abus, l'API limite le nombre de requêtes par période.

### Configuration

- **Limite** : 20 requêtes par minute (par IP ou API Key)
- **Environnement** : Activé uniquement en production (`DEBUG=false`)
- **Endpoints concernés** : `/predict`, `/predict/batch`

### Réponse en cas de dépassement

```json
{
  "error": "Rate limit exceeded",
  "message": "20 per 1 minute"
}
```

**Status code** : `429 Too Many Requests`

### Headers de rate limiting

Les réponses incluent des headers informatifs :

```http
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 15
X-RateLimit-Reset: 1672531200
```

---

## 📡 Endpoints

### 1. Health Check

**Vérifie l'état de l'API et du modèle ML.**

```http
GET /health
```

#### Réponse (200 OK)

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_type": "Pipeline",
  "version": "3.2.1"
}
```

#### Réponse en cas d'erreur (503 Service Unavailable)

```json
{
  "status": "unhealthy",
  "error": "Model not available",
  "message": "Failed to load model from HuggingFace Hub"
}
```

#### Exemple curl

```bash
curl -X GET http://localhost:8000/health
```

#### Cas d'usage

- Monitoring automatique (Kubernetes liveness/readiness probes)
- Vérification avant déploiement
- Tests d'intégration

---

### 2. Prédiction unitaire

**Prédit le risque de départ d'un employé à partir de ses données.**

```http
POST /predict
```

#### Headers requis

```http
Content-Type: application/json
X-API-Key: your-secret-key  (en production uniquement)
```

#### Corps de la requête (JSON)

Voir [Schémas Pydantic](#schémas-pydantic) pour la structure complète.

**Exemple minimal** :

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

#### Réponse (200 OK)

```json
{
  "prediction": 0,
  "probability_0": 0.85,
  "probability_1": 0.15,
  "risk_level": "Low"
}
```

**Champs de la réponse** :

- `prediction` : Classe prédite (0 = reste, 1 = part)
- `probability_0` : Probabilité de rester dans l'entreprise
- `probability_1` : Probabilité de quitter l'entreprise
- `risk_level` : Niveau de risque (`Low`, `Medium`, `High`)

#### Niveaux de risque

| Risk Level | Probabilité de départ | Action recommandée |
|------------|----------------------|-------------------|
| **Low** | < 0.3 | Aucune action |
| **Medium** | 0.3 - 0.7 | Surveillance |
| **High** | > 0.7 | Action urgente |

#### Exemple curl

```bash
curl -X POST http://localhost:8000/predict \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "genre": "M",
    "revenu_mensuel": 4500.0,
    "statut_marital": "Marié(e)",
    "departement": "Commercial",
    "poste": "Manager",
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
    "nombre_experiences_precedentes": 3,
    "nombre_heures_travailless": 80,
    "annee_experience_totale": 10,
    "annees_dans_l_entreprise": 5,
    "annees_dans_le_poste_actuel": 2
  }'
```

---

### 3. Prédiction batch (CSV)

**Traite un fichier CSV complet et retourne les prédictions pour tous les employés.**

```http
POST /predict/batch
```

#### Headers requis

```http
Content-Type: multipart/form-data
X-API-Key: your-secret-key  (en production uniquement)
```

#### Fichiers requis

L'endpoint attend **3 fichiers CSV** correspondant aux sources de données originales :

| Paramètre | Description | Colonnes clés |
|-----------|-------------|---------------|
| `sondage_file` | Données de satisfaction | `code_sondage`, `satisfaction_*`, `frequence_deplacement` |
| `eval_file` | Données d'évaluation | `eval_number`, `note_evaluation_*`, `heure_supplementaires` |
| `sirh_file` | Données RH | `id_employee`, `age`, `genre`, `revenu_mensuel`, `poste` |

#### Réponse (200 OK)

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

#### Exemple curl

```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "X-API-Key: your-secret-key" \
  -F "sondage_file=@data/extrait_sondage.csv" \
  -F "eval_file=@data/extrait_eval.csv" \
  -F "sirh_file=@data/extrait_sirh.csv"
```

#### Exemple Python

```python
import requests

url = "http://localhost:8000/predict/batch"
headers = {"X-API-Key": "your-secret-key"}

files = {
    "sondage_file": open("data/extrait_sondage.csv", "rb"),
    "eval_file": open("data/extrait_eval.csv", "rb"),
    "sirh_file": open("data/extrait_sirh.csv", "rb"),
}

response = requests.post(url, headers=headers, files=files)
result = response.json()

print(f"Total employés : {result['total_employees']}")
print(f"Risque élevé : {result['summary']['high_risk_count']}")
```

---

## 📊 Schémas Pydantic

### EmployeeInput

**Schéma d'entrée pour la prédiction unitaire.**

Pydantic valide automatiquement tous les champs selon leurs types et contraintes.

#### Données Sondage

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| `nombre_participation_pee` | `int` | 0-3 | Participations au Plan d'Épargne Entreprise |
| `nb_formations_suivies` | `int` | 0-6 | Nombre de formations suivies |
| `nombre_employee_sous_responsabilite` | `int` | 1 (fixe) | Employés sous responsabilité |
| `distance_domicile_travail` | `int` | 1-30 | Distance domicile-travail (km) |
| `niveau_education` | `int` | 1-5 | Niveau d'éducation (1=Bac, 5=Doctorat) |
| `domaine_etude` | `enum` | Voir ci-dessous | Domaine d'études |
| `ayant_enfants` | `enum` | "Y" ou "N" | A des enfants |
| `frequence_deplacement` | `enum` | Voir ci-dessous | Fréquence des déplacements |

**Énumération `domaine_etude`** :
- `"Infra & Cloud"`
- `"Transformation Digitale"`
- `"Marketing"`
- `"Entrepreunariat"`
- `"Ressources Humaines"`
- `"Autre"`

**Énumération `frequence_deplacement`** :
- `"Aucun"`
- `"Occasionnel"`
- `"Frequent"`

#### Données Évaluation

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| `annees_depuis_la_derniere_promotion` | `int` | 0-15 | Années depuis dernière promotion |
| `annes_sous_responsable_actuel` | `int` | 0-17 | Années sous responsable actuel |
| `satisfaction_employee_environnement` | `int` | 1-4 | Satisfaction environnement travail |
| `note_evaluation_precedente` | `int` | 1-4 | Note évaluation année précédente |
| `niveau_hierarchique_poste` | `int` | 1-5 | Niveau hiérarchique du poste |
| `satisfaction_employee_nature_travail` | `int` | 1-4 | Satisfaction nature du travail |
| `satisfaction_employee_equipe` | `int` | 1-4 | Satisfaction travail en équipe |
| `satisfaction_employee_equilibre_pro_perso` | `int` | 1-4 | Satisfaction équilibre vie pro/perso |
| `note_evaluation_actuelle` | `int` | 3-4 | Note évaluation actuelle |
| `heure_supplementaires` | `enum` | "Oui" ou "Non" | Fait des heures supplémentaires |
| `augementation_salaire_precedente` | `float` | 0-100 | Augmentation salaire précédente (%) |

#### Données SIRH

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| `age` | `int` | 18-60 | Âge de l'employé |
| `genre` | `enum` | "M" ou "F" | Genre |
| `revenu_mensuel` | `float` | 1000-20000 | Revenu mensuel (€) |
| `statut_marital` | `enum` | Voir ci-dessous | Statut marital |
| `departement` | `enum` | Voir ci-dessous | Département |
| `poste` | `enum` | Voir ci-dessous | Intitulé du poste |
| `nombre_experiences_precedentes` | `int` | 0-9 | Nombre d'expériences précédentes |
| `nombre_heures_travailless` | `int` | 80 (fixe) | Heures travaillées/semaine |
| `annee_experience_totale` | `int` | 0-40 | Années d'expérience totale |
| `annees_dans_l_entreprise` | `int` | 0-40 | Années dans l'entreprise |
| `annees_dans_le_poste_actuel` | `int` | 0-18 | Années dans le poste actuel |

**Énumération `statut_marital`** :
- `"Célibataire"`
- `"Marié(e)"`
- `"Divorcé(e)"`

**Énumération `departement`** :
- `"Commercial"`
- `"Consulting"`
- `"Ressources Humaines"`

**Énumération `poste`** :
- `"Cadre Commercial"`
- `"Assistant de Direction"`
- `"Consultant"`
- `"Tech Lead"`
- `"Manager"`
- `"Senior Manager"`
- `"Représentant Commercial"`
- `"Directeur Technique"`
- `"Ressources Humaines"`

#### Pourquoi Pydantic ?

✅ **Validation automatique** : Rejette les données invalides avant le traitement  
✅ **Messages d'erreur clairs** : Indique exactement quel champ est invalide  
✅ **Type safety** : Garantit que les types sont corrects  
✅ **Documentation auto** : Génère automatiquement les schémas OpenAPI  
✅ **Performance** : Validation en C via Rust (très rapide)

**Exemple d'erreur de validation** :

```bash
# Requête avec âge invalide
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 150, ...}'

# Réponse (422 Unprocessable Entity)
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "age"],
      "msg": "Input should be less than or equal to 60",
      "input": 150,
      "ctx": {"le": 60}
    }
  ]
}
```

### PredictionOutput

**Schéma de sortie pour la prédiction.**

```python
class PredictionOutput(BaseModel):
    prediction: int  # 0 = reste, 1 = part
    probability_0: float  # Probabilité de rester (0-1)
    probability_1: float  # Probabilité de partir (0-1)
    risk_level: str  # "Low", "Medium", "High"
```

### HealthCheck

**Schéma pour le health check.**

```python
class HealthCheck(BaseModel):
    status: str  # "healthy" ou "unhealthy"
    model_loaded: bool  # Modèle chargé ou non
    model_type: str  # Type du modèle (ex: "Pipeline")
    version: str  # Version de l'API
```

### BatchPredictionOutput

**Schéma de sortie pour les prédictions batch.**

```python
class BatchPredictionOutput(BaseModel):
    total_employees: int  # Nombre total d'employés traités
    predictions: list[EmployeePrediction]  # Liste des prédictions
    summary: dict  # Résumé statistique
```

---

## 💡 Exemples d'utilisation

### 1. Test de santé de l'API

```bash
# Vérifier que l'API fonctionne
curl -X GET http://localhost:8000/health

# Réponse attendue
# {"status":"healthy","model_loaded":true,"model_type":"Pipeline","version":"3.2.1"}
```

### 2. Prédiction unitaire (développement)

```bash
# Sans authentification (DEBUG=true)
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### 3. Prédiction unitaire (production)

```bash
# Avec authentification (DEBUG=false)
export API_KEY="your-secret-key"

curl -X POST https://asi-engineer-oc-p5.hf.space/predict \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d @employee.json
```

**Contenu de `employee.json`** :

```json
{
  "age": 28,
  "genre": "F",
  "revenu_mensuel": 3200.0,
  "statut_marital": "Célibataire",
  "departement": "Consulting",
  "poste": "Consultant",
  "nombre_participation_pee": 1,
  "nb_formations_suivies": 3,
  "nombre_employee_sous_responsabilite": 1,
  "distance_domicile_travail": 10,
  "niveau_education": 4,
  "domaine_etude": "Transformation Digitale",
  "ayant_enfants": "N",
  "frequence_deplacement": "Frequent",
  "annees_depuis_la_derniere_promotion": 5,
  "annes_sous_responsable_actuel": 3,
  "satisfaction_employee_environnement": 2,
  "note_evaluation_precedente": 3,
  "niveau_hierarchique_poste": 1,
  "satisfaction_employee_nature_travail": 2,
  "satisfaction_employee_equipe": 3,
  "satisfaction_employee_equilibre_pro_perso": 1,
  "note_evaluation_actuelle": 3,
  "heure_supplementaires": "Oui",
  "augementation_salaire_precedente": 3.0,
  "nombre_experiences_precedentes": 1,
  "nombre_heures_travailless": 80,
  "annee_experience_totale": 4,
  "annees_dans_l_entreprise": 3,
  "annees_dans_le_poste_actuel": 2
}
```

### 4. Prédiction batch

```bash
# Traiter un dataset complet
curl -X POST http://localhost:8000/predict/batch \
  -H "X-API-Key: $API_KEY" \
  -F "sondage_file=@data/extrait_sondage.csv" \
  -F "eval_file=@data/extrait_eval.csv" \
  -F "sirh_file=@data/extrait_sirh.csv" \
  -o predictions.json

# Afficher le résumé
cat predictions.json | jq '.summary'
```

### 5. Exemple Python avec requests

```python
import requests
import json

# Configuration
API_URL = "http://localhost:8000/predict"
API_KEY = "your-secret-key"

# Données d'un employé
employee_data = {
    "age": 35,
    "genre": "M",
    "revenu_mensuel": 4500.0,
    "statut_marital": "Marié(e)",
    "departement": "Commercial",
    "poste": "Manager",
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
    "nombre_experiences_precedentes": 3,
    "nombre_heures_travailless": 80,
    "annee_experience_totale": 10,
    "annees_dans_l_entreprise": 5,
    "annees_dans_le_poste_actuel": 2
}

# Envoi de la requête
headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(API_URL, headers=headers, json=employee_data)

# Traitement de la réponse
if response.status_code == 200:
    result = response.json()
    print(f"Prédiction: {'Départ' if result['prediction'] == 1 else 'Reste'}")
    print(f"Probabilité de départ: {result['probability_1']:.2%}")
    print(f"Niveau de risque: {result['risk_level']}")
else:
    print(f"Erreur {response.status_code}: {response.text}")
```

### 6. Exemple JavaScript (Node.js)

```javascript
const axios = require('axios');

// Configuration
const API_URL = 'http://localhost:8000/predict';
const API_KEY = 'your-secret-key';

// Données d'un employé
const employeeData = {
  age: 35,
  genre: "M",
  revenu_mensuel: 4500.0,
  statut_marital: "Marié(e)",
  departement: "Commercial",
  poste: "Manager",
  // ... autres champs
};

// Envoi de la requête
axios.post(API_URL, employeeData, {
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  }
})
.then(response => {
  const result = response.data;
  console.log(`Prédiction: ${result.prediction === 1 ? 'Départ' : 'Reste'}`);
  console.log(`Probabilité: ${(result.probability_1 * 100).toFixed(2)}%`);
  console.log(`Risque: ${result.risk_level}`);
})
.catch(error => {
  console.error('Erreur:', error.response?.data || error.message);
});
```

### 7. Exemple Postman

**Configuration de la requête Postman** :

1. **Méthode** : `POST`
2. **URL** : `http://localhost:8000/predict`
3. **Headers** :
   - `Content-Type`: `application/json`
   - `X-API-Key`: `your-secret-key`
4. **Body** (raw JSON) : Copier le JSON de `employee.json` ci-dessus
5. **Tests** (optionnel) :

```javascript
// Vérifier le statut
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Vérifier la structure
pm.test("Response has prediction", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('prediction');
    pm.expect(jsonData).to.have.property('probability_0');
    pm.expect(jsonData).to.have.property('probability_1');
    pm.expect(jsonData).to.have.property('risk_level');
});

// Vérifier les probabilités
pm.test("Probabilities sum to 1", function () {
    var jsonData = pm.response.json();
    var sum = jsonData.probability_0 + jsonData.probability_1;
    pm.expect(sum).to.be.closeTo(1, 0.01);
});
```

---

## ❌ Codes d'erreur

### Codes HTTP standards

| Code | Status | Description | Exemple |
|------|--------|-------------|---------|
| **200** | OK | Succès | Prédiction réussie |
| **401** | Unauthorized | API Key invalide ou manquante | Header `X-API-Key` absent |
| **422** | Unprocessable Entity | Données invalides | Âge > 60, champ manquant |
| **429** | Too Many Requests | Rate limit dépassé | > 20 req/min |
| **500** | Internal Server Error | Erreur serveur | Modèle crashé |
| **503** | Service Unavailable | Service indisponible | Modèle non chargé |

### Détails des erreurs de validation (422)

**Exemple : Champ manquant**

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "age"],
      "msg": "Field required",
      "input": {...}
    }
  ]
}
```

**Exemple : Type invalide**

```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["body", "age"],
      "msg": "Input should be a valid integer",
      "input": "trente-cinq"
    }
  ]
}
```

**Exemple : Valeur hors limites**

```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "age"],
      "msg": "Input should be less than or equal to 60",
      "input": 75,
      "ctx": {"le": 60}
    }
  ]
}
```

**Exemple : Énumération invalide**

```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["body", "genre"],
      "msg": "Input should be 'M' or 'F'",
      "input": "Homme",
      "ctx": {"expected": "'M' or 'F'"}
    }
  ]
}
```

---

## ✅ Bonnes pratiques

### Pour les développeurs

1. **Tester localement** : Utilisez `/docs` pour tester interactivement
2. **Valider les données** : Pydantic rejette automatiquement les données invalides
3. **Gérer les erreurs** : Toujours vérifier le status code HTTP
4. **Logger les requêtes** : Activer le logging pour debugging
5. **Respecter le rate limit** : Implémenter un backoff exponentiel

### Pour les utilisateurs de l'API

1. **Utiliser HTTPS en production** : Sécuriser les communications
2. **Protéger l'API Key** : Ne jamais la commiter dans Git
3. **Gérer le cache** : Mettre en cache les prédictions fréquentes
4. **Monitoring** : Surveiller `/health` régulièrement
5. **Batch quand possible** : Utiliser `/predict/batch` pour volumes importants

### Exemple de gestion d'erreurs (Python)

```python
import requests
import time

def predict_with_retry(employee_data, max_retries=3):
    """Appelle l'API avec retry automatique."""
    url = "http://localhost:8000/predict"
    headers = {"X-API-Key": "your-key", "Content-Type": "application/json"}
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=employee_data)
            
            # Succès
            if response.status_code == 200:
                return response.json()
            
            # Rate limit → retry avec backoff
            elif response.status_code == 429:
                wait_time = 2 ** attempt  # Backoff exponentiel
                print(f"Rate limit, attente {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            # Erreur validation → pas de retry
            elif response.status_code == 422:
                print(f"Données invalides: {response.json()}")
                return None
            
            # Erreur serveur → retry
            elif response.status_code >= 500:
                print(f"Erreur serveur, retry {attempt + 1}/{max_retries}")
                time.sleep(1)
                continue
            
            # Autre erreur
            else:
                print(f"Erreur {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Erreur connexion: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                return None
    
    print("Échec après plusieurs tentatives")
    return None
```

---

## 🔗 Ressources additionnelles

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **Repo GitHub** : https://github.com/chaton59/OC_P5
- **HuggingFace Space** : https://asi-engineer-oc-p5.hf.space
- **Documentation FastAPI** : https://fastapi.tiangolo.com
- **Documentation Pydantic** : https://docs.pydantic.dev

---

## 📞 Support

Pour toute question ou problème :

1. Consulter la documentation Swagger `/docs`
2. Vérifier les logs de l'API
3. Ouvrir une issue sur GitHub
4. Contacter l'équipe de développement

---

**Version du document** : 3.2.1  
**Dernière mise à jour** : 1 janvier 2026
