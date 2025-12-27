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
- 📊 Probabilités et niveau de risque (Low/Medium/High)
- 🔐 Authentification API Key
- 📝 Logs structurés JSON
- 🛡️ Rate limiting (20 req/min)
- 📚 Documentation OpenAPI/Swagger

## 🔗 Endpoints

- **Docs** : `/docs` - Documentation interactive
- **Health** : `/health` - Status de l'API
- **Predict** : `/predict` - Prédiction de turnover

## 🚀 Utilisation

```bash
# Health check
curl https://asi-engineer-employee-turnover-api.hf.space/health

# Prédiction
curl -X POST https://asi-engineer-employee-turnover-api.hf.space/predict \
  -H "Content-Type: application/json" \
  -d '{
    "satisfaction_employee_environnement": 3,
    "satisfaction_employee_nature_travail": 4,
    ...
  }'
```

## 📚 Documentation complète

Voir [GitHub Repository](https://github.com/chaton59/OC_P5) pour la documentation complète.
