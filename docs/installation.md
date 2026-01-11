# 📦 Installation

Guide d'installation complète du projet Employee Turnover Prediction API.

---

## ⚙️ Prérequis

| Outil | Version | Installation |
|-------|---------|--------------|
| **Python** | 3.12+ | [python.org/downloads](https://www.python.org/downloads/) |
| **Poetry** | 1.7+ | `curl -sSL https://install.python-poetry.org \| python3 -` |
| **PostgreSQL** | 14+ | `sudo apt install postgresql` (Linux) |
| **Git** | 2.0+ | `sudo apt install git` |

---

## 🚀 Installation Rapide

```bash
# 1. Cloner le projet
git clone https://github.com/chaton59/OC_P5.git
cd OC_P5

# 2. Installer les dépendances
poetry install

# 3. Créer le fichier .env
cp .env.example .env

# 4. Lancer l'API
poetry run uvicorn api:app --reload
```

Accéder à : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📋 Installation Détaillée

### 1. Cloner le Repository

```bash
git clone https://github.com/chaton59/OC_P5.git
cd OC_P5
```

### 2. Installer les Dépendances avec Poetry

```bash
# Installer Poetry (si pas déjà installé)
curl -sSL https://install.python-poetry.org | python3 -

# Installer les dépendances du projet
poetry install

# Vérifier l'installation
poetry run python --version
```

**Dépendances installées** :
- FastAPI, Uvicorn (API REST)
- XGBoost, scikit-learn, imbalanced-learn (ML)
- Pydantic (validation)
- SQLAlchemy, psycopg2 (PostgreSQL)
- Gradio (interface web)

### 3. Configuration

#### Créer le fichier .env

```bash
cp .env.example .env
```

#### Contenu minimal du .env

```bash
# Mode développement (désactive l'authentification)
DEBUG=true

# Niveau de logs
LOG_LEVEL=INFO

# API
API_VERSION=3.3.0

# Modèle HuggingFace
HF_MODEL_REPO=ASI-Engineer/employee-turnover-model
MODEL_FILENAME=model/model.pkl
```

➡️ **Configuration complète** : Voir [configuration.md](configuration.md)

### 4. Base de Données PostgreSQL (Optionnel)

#### Option A : PostgreSQL local

```bash
# Installer PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Créer la base de données
sudo -u postgres createdb oc_p5_db
sudo -u postgres createuser ml_user -P  # Définir mot de passe

# Ajouter dans .env
DATABASE_URL=postgresql://ml_user:your_password@localhost:5432/oc_p5_db
```

#### Option B : Docker

```bash
docker run --name postgres-turnover \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=oc_p5_db \
  -e POSTGRES_USER=ml_user \
  -p 5432:5432 \
  -d postgres:14

# Ajouter dans .env
DATABASE_URL=postgresql://ml_user:mypassword@localhost:5432/oc_p5_db
```

#### Créer les tables

```bash
poetry run python scripts/create_db.py
```

### 5. Vérifier l'Installation

```bash
# Lancer les tests
poetry run pytest tests/ -v

# Vérifier le chargement du modèle
poetry run python -c "from src.models import load_model; print(load_model())"

# Lancer l'API
poetry run uvicorn api:app --reload
```

#### Tester l'API

```bash
# Health check
curl http://localhost:8000/health

# Réponse attendue :
# {"status":"healthy","model_loaded":true,"version":"3.3.0"}
```

---

## 🖥️ Interfaces Disponibles

Une fois l'API lancée :

| Interface | URL | Description |
|-----------|-----|-------------|
| **Swagger UI** | [localhost:8000/docs](http://localhost:8000/docs) | Documentation interactive |
| **ReDoc** | [localhost:8000/redoc](http://localhost:8000/redoc) | Documentation alternative |
| **Gradio UI** | [localhost:8000/ui](http://localhost:8000/ui) | Interface web utilisateur |
| **Health** | [localhost:8000/health](http://localhost:8000/health) | Vérification état API |

---

## 🔧 Installation Développement

Pour contribuer au projet :

```bash
# Installer avec dépendances dev
poetry install --with dev

# Installer les hooks pre-commit
poetry run pre-commit install

# Lancer les linters
poetry run black .
poetry run flake8 .

# Tests avec coverage
poetry run pytest --cov=. --cov-report=html
```

---

## 🐳 Installation Docker

```bash
# Build de l'image
docker build -t turnover-api .

# Lancer le container
docker run -p 8000:8000 \
  -e DEBUG=true \
  --name turnover-api \
  turnover-api

# Accéder à l'API
curl http://localhost:8000/health
```

---

## ❓ Troubleshooting

### Erreur : `poetry command not found`

```bash
# Ajouter Poetry au PATH
export PATH="$HOME/.local/bin:$PATH"

# Ou installer via pip
pip install poetry
```

### Erreur : `ModuleNotFoundError`

```bash
# Réinstaller les dépendances
poetry install --no-cache
```

### Erreur : Connexion PostgreSQL refusée

```bash
# Vérifier que PostgreSQL est démarré
sudo systemctl status postgresql

# Démarrer si nécessaire
sudo systemctl start postgresql
```

### Erreur : Le modèle ne se charge pas

```bash
# Vérifier la connexion internet (télécharge depuis HuggingFace)
curl https://huggingface.co

# Définir HF_MODEL_REPO dans .env
HF_MODEL_REPO=ASI-Engineer/employee-turnover-model
```

---

## ➡️ Prochaines Étapes

- ✅ [Configuration avancée](configuration.md)
- ✅ [Guide API](api.md)
- ✅ [Déploiement](deployment.md)

