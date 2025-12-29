---
title: Employee Turnover Prediction API
emoji: 👔
colorFrom: blue
colorTo: purple
sdk: gradio
pinned: true
license: mit
app_port: 7860
---


# Employee Turnover Prediction API 🚀 (v3.2.1)

API de prédiction du turnover des employés (XGBoost + SMOTE) avec endpoints batch, validation stricte et documentation à jour.

## 🎯 Fonctionnalités

- ✅ Prédiction de turnover (0 = reste, 1 = part)
- 📦 Endpoint batch CSV (3 fichiers bruts)
- 🎛️ Sliders Gradio et schémas Pydantic alignés sur les min/max réels
- 📊 Probabilités et niveau de risque (Low/Medium/High)
- 🔐 Authentification API Key (obligatoire)
- 📝 Logs structurés JSON
- 🛡️ Rate limiting (20 req/min)
- 📚 Documentation OpenAPI/Swagger


## 🔗 Endpoints

| Endpoint | Description |
|----------|-------------|
| `/docs` | Documentation interactive Swagger |
| `/health` | Status de l'API |
| `/ui` | Interface Gradio interactive |
| `/predict` | Prédiction unitaire (JSON, contraintes réelles) |
| `/predict/batch` | Prédiction batch (3 fichiers CSV bruts) |


## 🚀 Utilisation

### Prédiction unitaire (toutes contraintes appliquées)
```bash
curl -X POST https://asi-engineer-oc-p5-dev.hf.space/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
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

### Prédiction batch (3 fichiers CSV bruts)
```bash
curl -X POST https://asi-engineer-oc-p5-dev.hf.space/predict/batch \
  -H "X-API-Key: your-key" \
  -F "sondage_file=@extrait_sondage.csv" \
  -F "eval_file=@extrait_eval.csv" \
  -F "sirh_file=@extrait_sirh.csv"
```

**Réponse :**
```json
{
  "total_employees": 1470,
  "predictions": [...],
  "summary": {
    "total_stay": 1169,
    "total_leave": 301,
    "high_risk_count": 222
  }
}
```


## 📚 Documentation complète

Voir [docs/API.md](docs/API.md) ou le [GitHub Repository](https://github.com/chaton59/OC_P5) pour la documentation complète et les contraintes détaillées (min/max, enums, etc).
