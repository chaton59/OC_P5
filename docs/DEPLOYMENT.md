# 🚀 Déploiement

Guide de déploiement de l'API Employee Turnover sur HuggingFace Spaces.

## 📋 Architecture

```
GitHub (dev/main)
       │
       ▼ push
GitHub Actions (CI/CD)
       │
       ├─► Lint (Black, Flake8)
       ├─► Tests (pytest)
       ├─► Test API Server
       │
       ▼ success
HuggingFace Spaces
       │
       ├─► oc_p5-dev (branche dev)
       └─► oc_p5 (branche main)
```

## 🔧 Configuration requise

### Secrets GitHub
Configurez ces secrets dans `Settings > Secrets and variables > Actions` :

| Secret | Description |
|--------|-------------|
| `HF_TOKEN` | Token HuggingFace (write access) |
| `API_KEY` | Clé API pour les tests |

### Variables d'environnement HF Spaces
Dans les settings du Space HuggingFace :

| Variable | Valeur |
|----------|--------|
| `API_KEY` | Clé API production |
| `DEBUG` | `false` |
| `LOG_LEVEL` | `INFO` |

## 🐳 Docker

### Build local
```bash
docker build -t employee-turnover-api .
docker run -p 8000:8000 -e API_KEY=test-key employee-turnover-api
```

### Dockerfile
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY src/ ./src/
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔄 Pipeline CI/CD

Le fichier `.github/workflows/ci-cd.yml` définit 4 jobs :

### 1. Lint
- Black (formatage)
- Flake8 (qualité code)

### 2. Tests
- pytest avec couverture
- Upload Codecov

### 3. Test API Server
- Démarre l'API
- Test `/health`
- Test `/predict`

### 4. Deploy
- **dev** → `ASI-Engineer/oc_p5-dev`
- **main** → `ASI-Engineer/oc_p5`

## 📦 Déploiement manuel

```bash
# 1. Push sur dev
git push origin dev

# 2. Vérifier CI/CD
# https://github.com/chaton59/OC_P5/actions

# 3. Une fois OK, merger sur main
git checkout main
git merge dev
git push origin main
```

## 🔗 URLs de production

| Environnement | URL |
|---------------|-----|
| Dev | https://asi-engineer-oc-p5-dev.hf.space |
| Prod | https://asi-engineer-oc-p5.hf.space |
| Swagger (dev) | https://asi-engineer-oc-p5-dev.hf.space/docs |
| Gradio (dev) | https://asi-engineer-oc-p5-dev.hf.space/ui |

## 🔍 Monitoring

### Health check
```bash
curl https://asi-engineer-oc-p5-dev.hf.space/health
```

### Logs HuggingFace
Visibles dans l'onglet "Logs" du Space.

### Format des logs (JSON)
```json
{
  "timestamp": "2025-12-27 00:00:00",
  "level": "INFO",
  "message": "Request POST /predict",
  "status_code": 200,
  "duration_ms": 45.2
}
```

## ⚠️ Troubleshooting

### Build échoue
- Vérifier `requirements.txt` est à jour
- `poetry export -f requirements.txt --output requirements.txt --without-hashes`

### Tests échouent
- Vérifier que le payload de test correspond au schéma
- Voir les logs GitHub Actions

### Space ne démarre pas
- Vérifier les logs HuggingFace
- Vérifier que `HF_TOKEN` a les bons droits
