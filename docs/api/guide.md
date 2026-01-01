# Guide Complet de l'API

!!! info "Documentation Complète"
    Cette page est extraite du guide complet [API_GUIDE.md](../API_GUIDE.md). 
    Pour la version la plus à jour, consultez le fichier source.

## Vue d'ensemble

L'API Employee Turnover Prediction expose un modèle de Machine Learning via une interface REST moderne construite avec **FastAPI**. Elle permet de prédire la probabilité qu'un employé quitte l'entreprise à partir de 29 variables RH.

### Caractéristiques

- ✅ **Validation automatique** avec Pydantic (29 champs)
- ✅ **Authentification** par API Key (production)
- ✅ **Rate limiting** (20 requêtes/minute)
- ✅ **Logs structurés** (JSON)
- ✅ **Documentation interactive** (Swagger/ReDoc)
- ✅ **Prédictions unitaires et batch** (CSV)

### URLs

| Environnement | URL | Authentification |
|---------------|-----|------------------|
| **Production** | https://asi-engineer-oc-p5.hf.space | API Key requise |
| **Développement** | https://asi-engineer-oc-p5-dev.hf.space | DEBUG mode (pas d'auth) |
| **Local** | http://localhost:8000 | Selon .env |

---

## 🏥 Health Check

### Endpoint

```
GET /health
```

### Description

Vérifie que l'API et le modèle ML sont opérationnels. Pas d'authentification requise.

### Réponse

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_type": "Pipeline",
  "version": "3.2.1"
}
```

### Exemple curl

```bash
curl https://asi-engineer-oc-p5.hf.space/health
```

---

## 🔮 Prédiction Unitaire

### Endpoint

```
POST /predict
Content-Type: application/json
X-API-Key: your-secret-key  # Requis en production
```

### Description

Prédit le risque de turnover pour un employé unique à partir de ses données RH.

### Payload

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

**Interprétation** :
- `prediction` : 0 = reste, 1 = part
- `probability_0` : Probabilité de rester (85%)
- `probability_1` : Probabilité de partir (15%)
- `risk_level` : Low (<30%), Medium (30-70%), High (>70%)

### Exemples

=== "curl Production"

    ```bash
    curl -X POST "https://asi-engineer-oc-p5.hf.space/predict" \
      -H "X-API-Key: your-secret-key" \
      -H "Content-Type: application/json" \
      -d '{
        "age": 35,
        "revenu_mensuel": 4500,
        "departement": "Commercial",
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_equilibre_pro_perso": 2,
        "satisfaction_employee_environnement": 3,
        "niveau_education": 3,
        "domaine_etude": "Infra & Cloud",
        "genre": "M",
        "statut_marital": "Marié(e)",
        "poste": "Manager",
        "ayant_enfants": "Y",
        "heure_supplementaires": "Non",
        "frequence_deplacement": "Occasionnel",
        "nombre_participation_pee": 0,
        "nb_formations_suivies": 2,
        "nombre_employee_sous_responsabilite": 1,
        "distance_domicile_travail": 15,
        "annees_depuis_la_derniere_promotion": 2,
        "annes_sous_responsable_actuel": 5,
        "note_evaluation_precedente": 4,
        "niveau_hierarchique_poste": 2,
        "note_evaluation_actuelle": 4,
        "augementation_salaire_precedente": 5.5,
        "nombre_experiences_precedentes": 3,
        "nombre_heures_travailless": 80,
        "annee_experience_totale": 10,
        "annees_dans_l_entreprise": 5,
        "annees_dans_le_poste_actuel": 2
      }'
    ```

=== "Python"

    ```python
    import requests

    url = "https://asi-engineer-oc-p5.hf.space/predict"
    headers = {
        "X-API-Key": "your-secret-key",
        "Content-Type": "application/json"
    }
    
    employee_data = {
        "age": 35,
        "revenu_mensuel": 4500,
        "departement": "Commercial",
        # ... autres champs
    }
    
    response = requests.post(url, json=employee_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Prédiction: {result['prediction']}")
        print(f"Risque de départ: {result['risk_level']}")
        print(f"Probabilité: {result['probability_1']*100:.1f}%")
    else:
        print(f"Erreur {response.status_code}: {response.text}")
    ```

=== "JavaScript"

    ```javascript
    const url = "https://asi-engineer-oc-p5.hf.space/predict";
    
    const employeeData = {
      age: 35,
      revenu_mensuel: 4500,
      departement: "Commercial",
      // ... autres champs
    };
    
    fetch(url, {
      method: "POST",
      headers: {
        "X-API-Key": "your-secret-key",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(employeeData)
    })
    .then(response => response.json())
    .then(data => {
      console.log("Prédiction:", data.prediction);
      console.log("Niveau de risque:", data.risk_level);
      console.log("Probabilité de départ:", (data.probability_1 * 100).toFixed(1) + "%");
    })
    .catch(error => console.error("Erreur:", error));
    ```

---

## 📦 Prédiction Batch

### Endpoint

```
POST /predict/batch
X-API-Key: your-secret-key  # Requis en production
```

### Description

Traite plusieurs employés en une seule requête via 3 fichiers CSV (format brut du dataset).

### Fichiers requis

1. **sondage_file** : Données de satisfaction
2. **eval_file** : Évaluations de performance
3. **sirh_file** : Données RH administratives

### Exemple curl

```bash
curl -X POST "https://asi-engineer-oc-p5.hf.space/predict/batch" \
  -H "X-API-Key: your-secret-key" \
  -F "sondage_file=@data/extrait_sondage.csv" \
  -F "eval_file=@data/extrait_eval.csv" \
  -F "sirh_file=@data/extrait_sirh.csv"
```

### Réponse

```json
{
  "total_employees": 1470,
  "predictions": [
    {
      "employee_id": 1,
      "prediction": 1,
      "probability_leave": 0.84,
      "risk_level": "High"
    },
    {
      "employee_id": 2,
      "prediction": 0,
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

---

## 🔐 Authentification

### Mode Développement (DEBUG=true)

API Key **non requise**. Pratique pour tests locaux.

```bash
# .env
DEBUG=true
```

### Mode Production (DEBUG=false)

API Key **requise** dans le header `X-API-Key`.

```bash
# .env
DEBUG=false
API_KEY=your-secret-key-here
```

### Générer une API Key

```python
import secrets
api_key = secrets.token_urlsafe(32)
print(f"API_KEY={api_key}")
```

### Erreur 401

```json
{
  "detail": "Missing API Key"
}
```

---

## 🛡️ Rate Limiting

**Limite** : 20 requêtes/minute par IP ou API Key (production uniquement).

**Réponse 429** (dépassement) :

```json
{
  "error": "Rate limit exceeded",
  "message": "20 per 1 minute"
}
```

**Désactivation** : `DEBUG=true` désactive le rate limiting.

---

## ❌ Gestion des Erreurs

### Codes HTTP

| Code | Signification | Cause commune |
|------|---------------|---------------|
| **200** | Succès | Requête valide |
| **400** | Bad Request | Validation Pydantic échouée |
| **401** | Unauthorized | API Key manquante/invalide |
| **422** | Unprocessable Entity | Format JSON invalide |
| **429** | Too Many Requests | Rate limit dépassé |
| **500** | Internal Server Error | Erreur modèle ML |

### Exemple d'erreur 400

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

---

## 📚 Documentation Interactive

### Swagger UI

URL : `https://asi-engineer-oc-p5.hf.space/docs`

- Interface interactive pour tester les endpoints
- Génération automatique de code (curl, Python, etc.)
- Try it out avec authentification

### ReDoc

URL : `https://asi-engineer-oc-p5.hf.space/redoc`

- Documentation lisible et navigable
- Export PDF possible
- Vue d'ensemble des schémas

---

## 🔗 Liens Utiles

- **[Schémas Pydantic complets](schemas.md)** : Tous les champs avec contraintes
- **[Exemples d'utilisation](examples.md)** : Plus d'exemples dans différents langages
- **[Guide d'authentification](authentication.md)** : Configuration détaillée
- **[API_GUIDE.md complet](../API_GUIDE.md)** : Documentation exhaustive (981 lignes)
