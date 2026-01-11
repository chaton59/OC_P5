# 🚀 Déploiement

Guide de déploiement de l'API sur HuggingFace Spaces avec CI/CD automatisé.

---

## 📋 Architecture

```
GitHub Repository (dev/main)
    │
    ▼ Push
GitHub Actions (CI/CD)
    │
    ├─► Lint (Black + Flake8)
    ├─► Tests (pytest)
    └─► Test API Server
    │
    ▼ Success
HuggingFace Spaces
    │
    ├─► oc_p5-dev (branche dev)
    └─► oc_p5 (branche main)
```

---

## 🔧 Configuration Requise

### 1. Secrets GitHub

Configurer dans `Settings > Secrets and variables > Actions` :

| Secret | Description | Obtention |
|--------|-------------|-----------|
| `HF_TOKEN` | Token HuggingFace (write) | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| `API_KEY` | Clé API pour tests | Générer : `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

### 2. Variables HuggingFace Spaces

Dans les settings du Space :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `API_KEY` | Votre clé secrète | Authentification production |
| `DEBUG` | `false` | Mode production |
| `LOG_LEVEL` | `INFO` | Niveau de logs |

---

## 🌐 Environnements

| Environnement | Branche | URL | Authentification |
|---------------|---------|-----|------------------|
| **Dev** | `dev` | [asi-engineer-oc-p5-dev.hf.space](https://asi-engineer-oc-p5-dev.hf.space) | ❌ Désactivée |
| **Prod** | `main` | [asi-engineer-oc-p5.hf.space](https://asi-engineer-oc-p5.hf.space) | ✅ Requise |

---

## 🔄 Pipeline CI/CD

Le fichier `.github/workflows/ci-cd.yml` définit 4 jobs :

### 1. Lint (30s)

```yaml
- name: Black
  run: poetry run black . --check

- name: Flake8
  run: poetry run flake8 .
```

### 2. Tests (3 min)

```yaml
- name: Tests avec Coverage
  run: poetry run pytest tests/ --cov=. --cov-report=xml

- name: Upload Codecov
  uses: codecov/codecov-action@v3
```

### 3. Test API Server (2 min)

```yaml
- name: Démarrer l'API
  run: poetry run uvicorn api:app &

- name: Test Health
  run: curl http://localhost:8000/health

- name: Test Predict
  run: curl -X POST http://localhost:8000/predict -d @test_payload.json
```

### 4. Deploy (automatique)

```yaml
- name: Deploy to HF Spaces
  if: github.ref == 'refs/heads/main'
  run: |
    git push https://huggingface.co/spaces/ASI-Engineer/oc_p5 main
```

---

## 📦 Déploiement Manuel

### 1. Push sur Dev

```bash
git checkout dev
git add .
git commit -m "Feature: nouvelle fonctionnalité"
git push origin dev
```

### 2. Vérifier CI/CD

Aller sur [github.com/chaton59/OC_P5/actions](https://github.com/chaton59/OC_P5/actions)

**Vérifier** :
- ✅ Lint passed
- ✅ Tests passed (86/97)
- ✅ API Server started

### 3. Merger vers Main (Production)

```bash
git checkout main
git merge dev
git push origin main
```

**GitHub Actions déploie automatiquement sur Production.**

---

## 🐳 Docker

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code source
COPY app.py .
COPY src/ ./src/
COPY api.py .

# Port
EXPOSE 8000

# Démarrage
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build et Run Local

```bash
# Build
docker build -t turnover-api .

# Run
docker run -p 8000:8000 \
  -e API_KEY=your-key \
  -e DEBUG=false \
  --name turnover-api \
  turnover-api

# Tester
curl http://localhost:8000/health
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_KEY=${API_KEY}
      - DEBUG=false
      - DATABASE_URL=postgresql://ml_user:password@db:5432/oc_p5_db
    depends_on:
      - db

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=ml_user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=oc_p5_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier
curl http://localhost:8000/health
```

---

## 🔍 Monitoring

### Health Check

```bash
# Dev
curl https://asi-engineer-oc-p5-dev.hf.space/health

# Prod
curl https://asi-engineer-oc-p5.hf.space/health
```

**Réponse attendue** :

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "3.3.0"
}
```

### Logs HuggingFace Spaces

Visibles dans l'onglet "Logs" du Space.

**Format JSON structuré** :

```json
{
  "timestamp": "2026-01-11T18:00:00",
  "level": "INFO",
  "message": "Request POST /predict",
  "method": "POST",
  "path": "/predict",
  "status_code": 200,
  "duration_ms": 45.2,
  "prediction": "Oui",
  "probability": 0.78
}
```

### Métriques à Surveiller

| Métrique | Seuil d'Alerte | Action |
|----------|----------------|--------|
| **Taux d'erreur 5xx** | > 1% | Vérifier logs, redéployer |
| **Temps de réponse** | > 2s | Optimiser modèle/preprocessing |
| **Taux de 422** | > 5% | Revoir validation Pydantic |
| **Prédictions "Oui"** | > 40% | Vérifier données, drift ? |

---

## ⚠️ Troubleshooting

### Build Échoue

**Cause** : `requirements.txt` obsolète

```bash
# Régénérer requirements.txt
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Commit et push
git add requirements.txt
git commit -m "Update requirements.txt"
git push
```

### Tests Échouent

**Causes communes** :
- Payload de test invalide → Vérifier `tests/fixtures/`
- Modèle non chargé → Vérifier `HF_MODEL_REPO` dans .env

```bash
# Lancer tests localement
poetry run pytest tests/ -v

# Debug un test spécifique
poetry run pytest tests/test_api/test_api_predict.py -v
```

### Space Ne Démarre Pas

**Vérifier** :
1. Logs HuggingFace (onglet "Logs")
2. Secrets configurés correctement
3. `HF_TOKEN` a les droits write

```bash
# Tester le token localement
poetry run python -c "
from huggingface_hub import HfApi
api = HfApi()
print(api.whoami())
"
```

### Erreur 503 : Model Not Loaded

**Cause** : Modèle non téléchargé depuis HuggingFace

```bash
# Vérifier que le modèle existe
curl https://huggingface.co/ASI-Engineer/employee-turnover-model/resolve/main/model/model.pkl

# Forcer le rechargement
# Redémarrer le Space depuis l'interface HF
```

---

## 🔄 Workflow Complet

### Développement

```bash
# 1. Créer une branche feature
git checkout -b feature/nouvelle-fonctionnalite

# 2. Développer et tester localement
poetry run pytest tests/ -v

# 3. Commit et push
git add .
git commit -m "Feature: description"
git push origin feature/nouvelle-fonctionnalite

# 4. Créer une Pull Request vers dev
# GitHub Actions lance les tests automatiquement

# 5. Merger vers dev après validation
git checkout dev
git merge feature/nouvelle-fonctionnalite
git push origin dev

# 6. Tester sur oc_p5-dev
curl https://asi-engineer-oc-p5-dev.hf.space/health

# 7. Si OK, merger vers main
git checkout main
git merge dev
git push origin main

# 8. Déploiement automatique sur production
```

### Hotfix en Production

```bash
# 1. Créer branche hotfix depuis main
git checkout main
git checkout -b hotfix/correction-urgente

# 2. Corriger et tester
poetry run pytest tests/ -v

# 3. Merger directement vers main
git checkout main
git merge hotfix/correction-urgente
git push origin main

# 4. Déploiement automatique (5-7 min)

# 5. Backporter vers dev
git checkout dev
git merge main
git push origin dev
```

---

## 📊 Checklist de Déploiement

Avant chaque déploiement en production :

- [ ] Tests passent localement (`pytest`)
- [ ] Linting OK (`black` + `flake8`)
- [ ] Testé sur environnement dev
- [ ] `requirements.txt` à jour
- [ ] Secrets HuggingFace configurés
- [ ] Modèle uploadé sur HuggingFace Hub
- [ ] Documentation à jour
- [ ] CHANGELOG.md mis à jour

---

## 🔗 Liens Utiles

- **GitHub Actions** : [github.com/chaton59/OC_P5/actions](https://github.com/chaton59/OC_P5/actions)
- **HF Space Dev** : [huggingface.co/spaces/ASI-Engineer/oc_p5-dev](https://huggingface.co/spaces/ASI-Engineer/oc_p5-dev)
- **HF Space Prod** : [huggingface.co/spaces/ASI-Engineer/oc_p5](https://huggingface.co/spaces/ASI-Engineer/oc_p5)
- **HF Model** : [huggingface.co/ASI-Engineer/employee-turnover-model](https://huggingface.co/ASI-Engineer/employee-turnover-model)

---

## ➡️ Prochaines Étapes

- ✅ [Configuration](configuration.md)
- ✅ [API](api.md)

