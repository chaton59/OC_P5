---
title: Employee Turnover Prediction API
emoji: 👔
colorFrom: blue
colorTo: purple
sdk: docker
pinned: true
license: mit
app_port: 7860
---

# Employee Turnover Prediction API 🚀

API de prédiction du turnover des employés avec XGBoost + SMOTE.

## 🎯 Fonctionnalités

- ✅ Prédiction de turnover (0 = reste, 1 = part)
- 📦 **Nouveau** : Endpoint batch pour traiter vos fichiers CSV directement
- 📊 Probabilités et niveau de risque (Low/Medium/High)
- 🔐 Authentification API Key
- 📝 Logs structurés JSON
- 🛡️ Rate limiting (20 req/min)
- 📚 Documentation OpenAPI/Swagger

## 🔗 Endpoints

| Endpoint | Description |
|----------|-------------|
| `/docs` | Documentation interactive Swagger |
| `/health` | Status de l'API |
| `/ui` | Interface Gradio interactive |
| `/predict` | Prédiction unitaire (JSON) |
| `/predict/batch` | Prédiction batch (3 fichiers CSV) |

## 🚀 Utilisation

### Prédiction unitaire
```bash
curl -X POST https://asi-engineer-oc-p5-dev.hf.space/predict \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_participation_pee": 0,
    "nb_formations_suivies": 2,
    "satisfaction_employee_environnement": 3,
    ...
  }'
```

### Prédiction batch (fichiers CSV)
```bash
curl -X POST https://asi-engineer-oc-p5-dev.hf.space/predict/batch \
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

Voir [GitHub Repository](https://github.com/chaton59/OC_P5) pour la documentation complète.
