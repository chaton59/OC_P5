# 🎯 Checklist de Merge dev → main

## ✅ Prérequis

- [x] Tous les tests passent sur dev (33/36)
- [x] Coverage à 88%
- [x] CI/CD pipeline configuré
- [x] Documentation à jour
- [x] Tag v2.2.0 créé
- [x] Push vers origin/dev effectué

## 🔍 Vérifications avant merge

### Tests
```bash
poetry run pytest tests/ -v
# ✅ 33 passed, 3 skipped
```

### Lint
```bash
poetry run black --check .
poetry run flake8 .
# ✅ No errors
```

### GitHub Actions
- [ ] Vérifier que CI/CD passe sur dev
- [ ] URL: https://github.com/chaton59/OC_P5/actions

## 🚀 Procédure de Merge

### Option A: Via GitHub (Recommandé)

1. **Créer Pull Request**
   ```
   - De: dev
   - Vers: main
   - Titre: "Release v2.2.0 - CI/CD & HF Spaces"
   ```

2. **Vérifier CI/CD**
   - Attendre que tous les checks passent
   - Vérifier les logs si erreurs

3. **Merger**
   - Cliquer "Merge pull request"
   - Option: "Squash and merge" ou "Create merge commit"

4. **Vérifier déploiement**
   - GitHub Actions lance deploy vers HF Spaces (Prod)
   - Vérifier logs de déploiement

### Option B: En ligne de commande

```bash
# 1. Se mettre sur main
git checkout main

# 2. Vérifier qu'on est à jour
git pull origin main

# 3. Merger dev
git merge dev --no-ff -m "Merge dev into main - Release v2.2.0"

# 4. Push
git push origin main

# 5. Vérifier GitHub Actions
# → Auto-deploy vers HF Spaces (Prod)
```

## 🌐 Après le merge

### 1. Vérifier HF Spaces (Prod)

**URL** : https://huggingface.co/spaces/ASI-Engineer/employee-turnover-api

**Tests** :
```bash
# Health check
curl https://asi-engineer-employee-turnover-api.hf.space/health

# Docs
open https://asi-engineer-employee-turnover-api.hf.space/docs
```

### 2. Vérifier GitHub Actions

**URL** : https://github.com/chaton59/OC_P5/actions

**Vérifier** :
- ✅ Lint job passed
- ✅ Test job passed
- ✅ Test API job passed
- ✅ Deploy HF Prod job passed

### 3. Tester l'API en production

```bash
# Test de prédiction
curl -X POST https://asi-engineer-employee-turnover-api.hf.space/predict \
  -H "Content-Type: application/json" \
  -d '{
    "satisfaction_employee_environnement": 3,
    "satisfaction_employee_nature_travail": 4,
    "satisfaction_employee_equipe": 5,
    "satisfaction_employee_equilibre_pro_perso": 3,
    "note_evaluation_actuelle": 85,
    "annees_depuis_la_derniere_promotion": 2,
    "nombre_formations_realisees": 3,
    "age": 35,
    "genre": "M",
    "revenu_mensuel": 5500,
    "statut_marital": "Marié(e)",
    "departement": "Commercial",
    "poste": "Manager",
    "domaine_etude": "Marketing",
    "frequence_deplacement": "Occasionnel",
    "nombre_experiences_precedentes": 2,
    "nombre_heures_travailless": 45,
    "annee_experience_totale": 10,
    "annees_dans_l_entreprise": 5,
    "annees_dans_le_poste_actuel": 3
  }'
```

## 📊 Validation finale

- [ ] API répond sur HF Spaces (Prod)
- [ ] Endpoint /health retourne "healthy"
- [ ] Endpoint /predict fonctionne
- [ ] Documentation /docs accessible
- [ ] Logs GitHub Actions sans erreur
- [ ] Tag v2.2.0 visible sur GitHub

## 🎉 Après validation

### Communication
- Mettre à jour README sur GitHub
- Annoncer le déploiement (si applicable)
- Documenter les changements

### Suivi
- Monitorer les logs HF Spaces
- Vérifier les métriques (requests, latency)
- Collecter les feedbacks

## ⚠️ En cas de problème

### Rollback rapide
```bash
# Si problème critique en prod
git checkout main
git revert HEAD
git push origin main
```

### Debug
```bash
# Voir les logs HF Spaces
# → HuggingFace Spaces > Logs tab

# Voir les logs GitHub Actions
# → Actions > [Run] > [Job] > Logs
```

## 📝 Checklist post-merge

- [ ] Dev et main synchronisés
- [ ] Production fonctionne
- [ ] Tests passent sur main
- [ ] Documentation à jour
- [ ] Release notes publiées

---

**Date** : 26 décembre 2025  
**Version** : 2.2.0  
**Responsable** : chaton59
