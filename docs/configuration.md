# Configuration de l'API

Ce guide décrit les options de configuration disponibles pour l'API.

## Fichier .env

L'API utilise un fichier `.env` pour la configuration. Créez-le à partir du template :

```bash
cp .env.example .env
```

## Variables d'environnement

### Mode DEBUG

```bash
DEBUG=true  # ou false
```

**Impact** :
- `DEBUG=true` : Authentification désactivée, logs détaillés
- `DEBUG=false` : Authentification requise, mode production

!!! warning "Production"
    Toujours utiliser `DEBUG=false` en production.

### API Key

```bash
API_KEY=your-secret-key-here
```

**Génération** :

```python
import secrets
print(secrets.token_urlsafe(32))
```

### Niveau de Logs

```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**Recommandations** :
- Développement : `DEBUG`
- Production : `INFO`
- Troubleshooting : `DEBUG`

### Modèle HuggingFace

```bash
HF_MODEL_REPO=ASI-Engineer/employee-turnover-model
MODEL_FILENAME=model/model.pkl
```

**Valeurs par défaut** :
- Repo : `ASI-Engineer/employee-turnover-model`
- Fichier : `model/model.pkl`

### Base de Données PostgreSQL

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=employee_turnover
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
```

**Avec Docker** :

```bash
docker run --name postgres-turnover \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=employee_turnover \
  -p 5432:5432 \
  -d postgres:14
```

---

## Configuration Avancée

### Logging

Fichiers de logs :
- `logs/api.log` : Tous les logs
- `logs/error.log` : Erreurs uniquement

Format JSON structuré :

```json
{
  "timestamp": "2026-01-01T10:30:45",
  "level": "INFO",
  "logger": "employee_turnover_api",
  "message": "Request POST /predict",
  "method": "POST",
  "path": "/predict",
  "status_code": 200,
  "duration_ms": 23.45
}
```

### Rate Limiting

Configuration dans `src/rate_limit.py` :

```python
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["20/minute"]
)
```

**Personnalisation** :
- Modifier `default_limits`
- Ajouter des limites par endpoint

### CORS

Configuration dans `api.py` :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production : liste d'origins spécifiques
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Exemple .env Complet

```bash
# Mode
DEBUG=false

# Authentification
API_KEY=your-super-secret-key-32-chars-min

# Logs
LOG_LEVEL=INFO

# Modèle ML
HF_MODEL_REPO=ASI-Engineer/employee-turnover-model
MODEL_FILENAME=model/model.pkl

# Base de données
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=employee_turnover
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure-password-here
```

---

## Validation de Configuration

### Vérifier les variables

```bash
poetry run python -c "from src.config import get_settings; s = get_settings(); print(f'DEBUG={s.DEBUG}, API_VERSION={s.API_VERSION}')"
```

### Tester la connexion DB

```bash
poetry run python scripts/create_db.py
```

### Tester le chargement du modèle

```bash
poetry run python -c "from src.models import load_model; model = load_model(); print(f'Modèle chargé: {type(model)}')"
```

---

## 🔗 Liens Utiles

- [Installation](installation.md)
- [Quickstart](quickstart.md)
- [Déploiement](deployment/overview.md)
