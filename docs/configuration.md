# ⚙️ Configuration

Guide de configuration de l'API Employee Turnover Prediction.

---

## 📋 Vue d'Ensemble

L'API utilise un fichier `.env` pour toute la configuration.

---

## 🔧 Fichier .env

### Création

```bash
cp .env.example .env
```

### Configuration Minimale

```bash
# Mode développement (sans authentification)
DEBUG=true

# Niveau de logs
LOG_LEVEL=INFO

# Version de l'API
API_VERSION=3.3.0

# Modèle HuggingFace
HF_MODEL_REPO=ASI-Engineer/employee-turnover-model
MODEL_FILENAME=model/model.pkl
```

---

## 🔐 Variables d'Environnement

### Mode DEBUG

```bash
DEBUG=true  # ou false
```

| DEBUG | Authentification | Rate Limiting | Logs | Usage |
|-------|------------------|---------------|------|-------|
| `true` | ❌ Désactivée | ❌ Désactivé | Détaillés | Développement |
| `false` | ✅ Requise | ✅ 20 req/min | Standards | Production |

⚠️ **Production** : Toujours `DEBUG=false`

---

### API Key

```bash
API_KEY=your-secret-key-here
```

**Génération sécurisée** :

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Résultat (exemple)
# XqR8kL3mN9pT2vW5yZ7aB4cD6eF8gH0iJ
```

**Utilisation** :

```bash
curl -X POST https://api.example.com/predict \
  -H "X-API-Key: XqR8kL3mN9pT2vW5yZ7aB4cD6eF8gH0iJ" \
  -d @data.json
```

---

### Niveau de Logs

```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

| Niveau | Contenu | Usage |
|--------|---------|-------|
| `DEBUG` | Tous les détails (requêtes, variables, traces) | Développement |
| `INFO` | Événements principaux (requêtes, prédictions) | **Production** |
| `WARNING` | Avertissements non-bloquants | Production |
| `ERROR` | Erreurs bloquantes | Production |
| `CRITICAL` | Erreurs fatales | Production |

**Recommandation** : `INFO` en production

---

### Modèle HuggingFace

```bash
HF_MODEL_REPO=ASI-Engineer/employee-turnover-model
MODEL_FILENAME=model/model.pkl
```

**Valeurs par défaut** : OK pour la plupart des cas

**Changement** : Utile pour tester un nouveau modèle

```bash
# Modèle de test
HF_MODEL_REPO=votre-username/votre-modele-test
MODEL_FILENAME=model/model_v2.pkl
```

---

### Base de Données PostgreSQL

```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

**Exemple local** :

```bash
DATABASE_URL=postgresql://ml_user:mypassword@localhost:5432/oc_p5_db
```

**Exemple Docker** :

```bash
DATABASE_URL=postgresql://ml_user:mypassword@postgres-container:5432/oc_p5_db
```

**Composants** :
- `user` : Utilisateur PostgreSQL
- `password` : Mot de passe
- `host` : Hôte (localhost ou nom du container)
- `port` : Port (par défaut 5432)
- `database` : Nom de la base

---

### API Server

```bash
API_HOST=0.0.0.0  # Écouter sur toutes les interfaces
API_PORT=8000     # Port par défaut
```

**Local** : `0.0.0.0` permet l'accès depuis l'extérieur  
**Production** : Géré automatiquement par HuggingFace Spaces

---

## 📄 Exemple .env Complet

### Développement

```bash
# ===== MODE =====
DEBUG=true

# ===== AUTHENTIFICATION =====
API_KEY=dev-key-not-required

# ===== LOGS =====
LOG_LEVEL=DEBUG

# ===== API =====
API_VERSION=3.3.0
API_HOST=0.0.0.0
API_PORT=8000

# ===== MODÈLE =====
HF_MODEL_REPO=ASI-Engineer/employee-turnover-model
MODEL_FILENAME=model/model.pkl

# ===== BASE DE DONNÉES =====
DATABASE_URL=postgresql://ml_user:devpassword@localhost:5432/oc_p5_db
```

### Production

```bash
# ===== MODE =====
DEBUG=false

# ===== AUTHENTIFICATION =====
API_KEY=XqR8kL3mN9pT2vW5yZ7aB4cD6eF8gH0iJ

# ===== LOGS =====
LOG_LEVEL=INFO

# ===== API =====
API_VERSION=3.3.0
API_HOST=0.0.0.0
API_PORT=8000

# ===== MODÈLE =====
HF_MODEL_REPO=ASI-Engineer/employee-turnover-model
MODEL_FILENAME=model/model.pkl

# ===== BASE DE DONNÉES =====
DATABASE_URL=postgresql://ml_user:securepassword123@db.example.com:5432/oc_p5_db
```

---

## 🗄️ Configuration PostgreSQL

### Installation Locale

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Démarrer le service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Créer la Base de Données

```bash
# Se connecter en tant que postgres
sudo -u postgres psql

# Créer l'utilisateur
CREATE USER ml_user WITH PASSWORD 'mypassword';

# Créer la base
CREATE DATABASE oc_p5_db OWNER ml_user;

# Donner les droits
GRANT ALL PRIVILEGES ON DATABASE oc_p5_db TO ml_user;

# Quitter
\q
```

### Configuration avec Docker

```bash
# Lancer PostgreSQL
docker run --name postgres-turnover \
  -e POSTGRES_USER=ml_user \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=oc_p5_db \
  -p 5432:5432 \
  -d postgres:14

# Vérifier
docker ps | grep postgres-turnover

# Ajouter dans .env
DATABASE_URL=postgresql://ml_user:mypassword@localhost:5432/oc_p5_db
```

### Créer les Tables

```bash
poetry run python scripts/create_db.py
```

---

## 🔍 Validation de Configuration

### Vérifier les Variables

```bash
poetry run python -c "
from src.config import get_settings
s = get_settings()
print(f'DEBUG={s.DEBUG}')
print(f'API_VERSION={s.API_VERSION}')
print(f'LOG_LEVEL={s.LOG_LEVEL}')
print(f'API_KEY_REQUIRED={s.is_api_key_required}')
"
```

### Tester la Connexion PostgreSQL

```bash
# Avec psql
psql -h localhost -U ml_user -d oc_p5_db -c "SELECT 1;"

# Avec Python
poetry run python -c "
from sqlalchemy import create_engine
from src.config import get_settings
s = get_settings()
engine = create_engine(s.DATABASE_URL)
print('Connexion OK')
"
```

### Tester le Chargement du Modèle

```bash
poetry run python -c "
from src.models import load_model
model = load_model()
print(f'Modèle chargé: {type(model)}')
"
```

---

## 🔐 Sécurité

### Bonnes Pratiques

- ✅ Ne JAMAIS commiter le fichier `.env`
- ✅ Utiliser `.env.example` comme template (sans secrets)
- ✅ Générer des API Keys sécurisées (32+ caractères)
- ✅ Changer les mots de passe par défaut
- ✅ Utiliser `DEBUG=false` en production

### Fichier .gitignore

```bash
# .gitignore
.env
.env.local
.env.production
*.env
```

### Variables d'Environnement HuggingFace

Configurer dans Settings > Variables :

| Variable | Valeur | Visibilité |
|----------|--------|------------|
| `API_KEY` | Clé secrète | 🔒 Secret |
| `DEBUG` | `false` | 👁️ Public |
| `LOG_LEVEL` | `INFO` | 👁️ Public |
| `DATABASE_URL` | URL complète | 🔒 Secret |

---

## 📊 Logging

### Configuration Avancée

Modifier `src/logger.py` pour personnaliser :

```python
# Format des logs
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/api.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
}
```

### Fichiers de Logs

| Fichier | Contenu | Rotation |
|---------|---------|----------|
| `logs/api.log` | Tous les logs | 10 MB, 5 backups |
| `logs/error.log` | Erreurs uniquement | 10 MB, 5 backups |

---

## 🔗 Liens Utiles

- [Installation](installation.md)
- [API](api.md)
- [Déploiement](deployment.md)
