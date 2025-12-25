---
title: Employee Turnover Prediction - DEV
emoji: 🎯
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
---

# 🎯 Employee Turnover Prediction - Environment DEV

Interface de test pour prédire le risque de départ des employés.

## 🚀 Modèle

- **Algorithme**: XGBoost avec RandomizedSearchCV
- **Équilibrage**: SMOTE pour classes déséquilibrées (ratio 5:1)
- **Tracking**: MLflow pour versioning et reproductibilité
- **Métriques**: Optimisé pour F1-Score

## 📊 Utilisation

1. Ajustez les paramètres de l'employé (satisfaction, évaluation, projets, etc.)
2. Cliquez sur "Prédire le risque de départ"
3. Obtenez la probabilité de turnover et les recommandations

## 🔧 Développement

Ce Space est synchronisé automatiquement via CI/CD depuis la branche `dev` du repository GitHub.

**Repository**: [chaton59/OC_P5](https://github.com/chaton59/OC_P5)
