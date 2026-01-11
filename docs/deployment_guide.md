# 🚀 Guide de Déploiement

Guide minimal pour déployer l'API sur HuggingFace Spaces avec CI/CD automatisé.

## Architecture de Déploiement

```
GitHub (dev/main)
    │
    ├─► GitHub Actions CI/CD
    │   ├── Lint (Black + Flake8)
    │   ├── Tests (pytest)
    │   └── Deploy
    │
    ├─► HF Spaces Dev (branche dev)
    └─► HF Spaces Prod (branche main)
```

---

## Environnements

| Environnement | Branche | URL | Auth | Rate Limit |
|---------------|---------|-----|------|------------|
| **Dev** | dev | [asi-engineer-oc-p5-dev.hf.space](https://asi-engineer-oc-p5-dev.hf.space) | ❌ | ❌ |
| **Prod** | main | [asi-engineer-oc-p5.hf.space](https://asi-engineer-oc-p5.hf.space) | ✅ | ✅ 20/min |

---

## Configuration Requise

### 1. Secrets GitHub

Dans `Settings > Secrets and variables > Actions` :

| Secret | Description | Génération |
|--------|-------------|------------|
| `HF_TOKEN` | Token HuggingFace (write) | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| `API_KEY` | Clé API pour tests | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

### 2. Variables HuggingFace Spaces

Dans les settings du Space (Production) :

```env
API_KEY=votre-clé-secrète-production
DEBUG=false
LOG_LEVEL=INFO
```

---

## Pipeline CI/CD

**Fichier** : `.github/workflows/ci-cd.yml`

### Étapes du Pipeline

```yaml
1. Lint (30s)
   - Black (formatage)
   - Flake8 (linting)

2. Tests (3 min)
   - pytest avec couverture
   - Upload Codecov

3. Test API Server (2 min)
   - Démarrage serveur
   - Test health endpoint
   - Test predict endpoint

4. Deploy (automatique)
   - Push vers HF Spaces si main
```

### Déclencheurs

- **Push** sur `dev` : CI/CD complet + deploy dev
- **Push** sur `main` : CI/CD complet + deploy prod
- **Pull Request** : CI/CD sans deploy

---

## Déploiement Step-by-Step

### 1. Développement

```bash
# Créer une branche
git checkout -b feature/nouvelle-fonctionnalite

# Développer et tester localement
poetry run pytest tests/
poetry run uvicorn api:app --reload

# Commit
git add .
git commit -m "feat: nouvelle fonctionnalité"
```

### 2. Déploiement Dev

```bash
# Merger dans dev
git checkout dev
git merge feature/nouvelle-fonctionnalite
git push origin dev

# GitHub Actions déploie automatiquement sur Dev
```

**Vérifier** : [github.com/chaton59/OC_P5/actions](https://github.com/chaton59/OC_P5/actions)

### 3. Tests sur Dev

```bash
# Health check
curl https://asi-engineer-oc-p5-dev.hf.space/health

# Prédiction (sans auth en dev)
curl -X POST https://asi-engineer-oc-p5-dev.hf.space/predict \
  -H "Content-Type: application/json" \
  -d @test_employee.json
```

### 4. Déploiement Production

```bash
# Merger dans main
git checkout main
git merge dev
git push origin main

# GitHub Actions déploie automatiquement sur Prod
```

### 5. Validation Production

```bash
# Health check
curl https://asi-engineer-oc-p5.hf.space/health

# Prédiction (avec API Key)
curl -X POST https://asi-engineer-oc-p5.hf.space/predict \
  -H "X-API-Key: votre-clé-production" \
  -H "Content-Type: application/json" \
  -d @test_employee.json
```

---

## Configuration HuggingFace Spaces

### Structure du Space

```
HF Space Root/
├── app.py              # Point d'entrée (Gradio + API)
├── api.py              # API FastAPI
├── requirements.txt    # Dépendances
├── src/                # Code source
├── ml_model/           # Modèle ML
└── data/               # Données CSV
```

### Variables d'Environnement

```bash
# Production
DEBUG=false
API_KEY=<secret-key-production>
LOG_LEVEL=INFO

# Dev
DEBUG=true
LOG_LEVEL=DEBUG
```

### Commande de Démarrage

HuggingFace Spaces exécute automatiquement `app.py` avec Gradio.

---

## Docker (Alternative)

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code source
COPY . .

# Port
EXPOSE 8000

# Démarrage
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build et Run

```bash
# Build
docker build -t turnover-api .

# Run
docker run -p 8000:8000 \
  -e API_KEY=your-key \
  -e DEBUG=false \
  turnover-api

# Test
curl http://localhost:8000/health
```

---

## Monitoring

### Health Check

```bash
# Automatique
curl https://asi-engineer-oc-p5.hf.space/health

# Réponse attendue
{
  "status": "healthy",
  "model_loaded": true,
  "model_type": "Pipeline",
  "version": "3.3.0"
}
```

### Logs

**HuggingFace Spaces** : Onglet "Logs" du Space  
**GitHub Actions** : [github.com/chaton59/OC_P5/actions](https://github.com/chaton59/OC_P5/actions)

**Format logs** : JSON structuré

```json
{
  "timestamp": "2026-01-11T17:30:45",
  "level": "INFO",
  "message": "Prediction made",
  "prediction": "Oui",
  "probability": 0.78
}
```

### Surveillance PostgreSQL

```bash
# Logs de prédictions
psql -h localhost -U ml_user -d oc_p5_db
SELECT COUNT(*) FROM ml_logs WHERE created_at > NOW() - INTERVAL '1 day';
```

---

## Gestion des Secrets

### .env (Local)

```env
# Ne JAMAIS commit ce fichier
DATABASE_URL=postgresql://ml_user:password@localhost:5432/oc_p5_db
API_KEY=dev-key-local
DEBUG=true
```

### GitHub Secrets

Utilisés par CI/CD, jamais exposés dans les logs.

### HuggingFace Secrets

Configurés dans Settings du Space, chiffrés par HF.

---

## Rollback

### Annuler un déploiement

```bash
# Revenir à un commit précédent
git checkout main
git revert HEAD
git push origin main

# Ou reset hard (attention)
git reset --hard <commit-sha>
git push origin main --force
```

### Redéploiement manuel

```bash
# Depuis GitHub Actions
# Re-run workflow depuis l'interface
```

---

## Troubleshooting

### Erreur : API Key manquante en production

**Solution** : Vérifier variables HF Spaces (API_KEY définie)

### Erreur : Modèle non chargé

**Solution** : Vérifier que `model.pkl` existe dans le repo

### Tests échouent en CI

**Solution** :
```bash
# Reproduire localement
poetry run pytest tests/ -v
```

### Déploiement bloqué

**Solution** : Vérifier logs GitHub Actions + HF Spaces

---

## Workflow Recommandé

1. **Développer** localement avec DEBUG=true
2. **Tester** localement : `pytest + uvicorn`
3. **Push dev** : Tests automatiques + deploy dev
4. **Valider** sur dev space
5. **Merger main** : Deploy production automatique
6. **Monitorer** health check + logs

---

## Ressources

- **GitHub Repository** : [github.com/chaton59/OC_P5](https://github.com/chaton59/OC_P5)
- **HF Space Dev** : [huggingface.co/spaces/ASI-Engineer/oc_p5-dev](https://huggingface.co/spaces/ASI-Engineer/oc_p5-dev)
- **HF Space Prod** : [huggingface.co/spaces/ASI-Engineer/oc_p5](https://huggingface.co/spaces/ASI-Engineer/oc_p5)
- **CI/CD Actions** : [github.com/chaton59/OC_P5/actions](https://github.com/chaton59/OC_P5/actions)
