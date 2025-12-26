# 🚀 Guide de Déploiement CI/CD

## 📋 Vue d'ensemble

Pipeline CI/CD complet pour déploiement automatique sur HuggingFace Spaces.

## 🏗️ Architecture du Pipeline

```
┌─────────────┐
│   Push      │
│  dev/main   │
└──────┬──────┘
       │
       ├──► 🔍 Lint (Black + Flake8)
       │
       ├──► 🧪 Tests (pytest + coverage)
       │
       ├──► 🚀 Test API (uvicorn + curl)
       │
       └──► 📦 Deploy HF Spaces
            ├─► Dev (si dev branch)
            └─► Prod (si main branch)
```

## 🔧 Configuration GitHub Actions

### Jobs du Pipeline

#### 1. 🔍 Lint
```yaml
- Black (format check)
- Flake8 (style check)
```

#### 2. 🧪 Tests
```yaml
- pytest avec coverage
- 33 tests automatisés
- Upload coverage vers Codecov
```

#### 3. 🚀 Test API
```yaml
- Démarre uvicorn en background
- Teste /health endpoint
- Teste /predict endpoint
- Vérifie réponses JSON
```

#### 4. 📦 Deploy HF Spaces
```yaml
Dev:
  - Branch: dev
  - Space: ASI-Engineer/employee-turnover-dev
  
Prod:
  - Branch: main
  - Space: ASI-Engineer/employee-turnover-api
```

## 🔐 Secrets GitHub requis

### HF_TOKEN
```bash
# Dans GitHub Settings > Secrets > Actions
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
```

**Comment obtenir** :
1. Aller sur https://huggingface.co/settings/tokens
2. Créer un token avec scope `write`
3. Copier dans GitHub secrets

## 🐳 Déploiement Docker

### Dockerfile
```dockerfile
FROM python:3.12-slim
- Installe dépendances système
- Installe requirements.txt
- Copie app.py + src/
- Expose port 8000
- Healthcheck intégré
- Workers: 2 (production)
```

### Variables d'environnement
```bash
DEBUG=false
API_KEY=${HF_SPACE_API_KEY}
LOG_LEVEL=INFO
```

## 🌐 HuggingFace Spaces

### Configuration

**README_HF.md** → README.md sur HF
```yaml
title: Employee Turnover Prediction API
sdk: docker
app_port: 8000
```

### URLs des Spaces

**Dev** : https://huggingface.co/spaces/ASI-Engineer/employee-turnover-dev
**Prod** : https://huggingface.co/spaces/ASI-Engineer/employee-turnover-api

### Auto-sync
✅ Push vers `dev` → Deploy automatique vers Dev Space
✅ Push vers `main` → Deploy automatique vers Prod Space

## 🚦 Workflow de déploiement

### Développement
```bash
# 1. Développer sur branch feature
git checkout -b feature/ma-feature

# 2. Commit + Push
git commit -m "feat: nouvelle feature"
git push origin feature/ma-feature

# 3. Pull Request vers dev
# → GitHub Actions lance tests

# 4. Merge vers dev
# → Auto-deploy vers HF Spaces (Dev)
```

### Production
```bash
# 1. Tests validés sur dev
git checkout main
git merge dev

# 2. Tag de version
git tag -a v2.2.0 -m "Release v2.2.0"

# 3. Push
git push origin main --tags

# → Auto-deploy vers HF Spaces (Prod)
```

## ✅ Vérification du déploiement

### Health Check
```bash
# Dev
curl https://asi-engineer-employee-turnover-dev.hf.space/health

# Prod
curl https://asi-engineer-employee-turnover-api.hf.space/health
```

### Test de prédiction
```bash
curl -X POST https://asi-engineer-employee-turnover-api.hf.space/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d @test_employee.json
```

## 📊 Monitoring

### GitHub Actions
- Voir les runs : `Actions` tab
- Logs détaillés par job
- Alertes par email si échec

### HuggingFace Spaces
- Logs : Dans l'interface HF Spaces
- Metrics : CPU, RAM, requests
- Status : Badge dans README

## 🐛 Troubleshooting

### Tests échouent
```bash
# Vérifier localement
poetry run pytest tests/ -v

# Vérifier logs GitHub Actions
# Actions > [Workflow Run] > [Job] > Logs
```

### Deploy échoue
```bash
# Vérifier HF_TOKEN
# Settings > Secrets > HF_TOKEN existe ?

# Vérifier logs deploy
# Actions > deploy-hf-prod/dev > Logs
```

### API ne démarre pas
```bash
# Vérifier Dockerfile
docker build -t test .
docker run -p 8000:8000 test

# Vérifier logs HF Spaces
# HF Spaces > Logs tab
```

## 🎯 Avantages du Pipeline

### Automatisation
✅ Tests automatiques
✅ Deploy automatique
✅ Pas d'intervention manuelle

### Qualité
✅ Lint obligatoire
✅ Coverage tracking
✅ Tests API réels

### Sécurité
✅ Secrets GitHub
✅ Validation avant deploy
✅ Environnements séparés (dev/prod)

### Scalabilité
✅ FastAPI > Gradio pour traffic
✅ Docker containerization
✅ Multi-workers (2 en prod)

## 📚 Ressources

- [GitHub Actions Docs](https://docs.github.com/actions)
- [HuggingFace Spaces](https://huggingface.co/docs/hub/spaces)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Version** : 2.2.0  
**Dernière mise à jour** : 26 décembre 2025
