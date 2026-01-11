# 🗄️ Configuration Base de Données

Guide de configuration et utilisation de PostgreSQL pour le projet.

## Vue d'Ensemble

Le projet utilise **PostgreSQL** pour stocker :
- Les données d'entraînement du modèle (`dataset`)
- Les logs des prédictions API (`ml_logs`)

## Configuration Initiale

### 1. Informations de Connexion

```bash
# Variables d'environnement (.env)
DATABASE_URL=postgresql://ml_user:password@localhost:5432/oc_p5_db

# Détails
Host: localhost (ou 127.0.0.1)
Port: 5432
Database: oc_p5_db
User: ml_user
Password: À définir
```

### 2. Création de la Base de Données

**Script automatique** : `scripts/create_db.py`

```bash
# Utilise SQLAlchemy pour créer automatiquement les tables
python scripts/create_db.py
```

**Sortie attendue :**
```
✅ Base de données et tables créées avec succès !
📊 Tables créées :
   - dataset : Stockage des données d'entraînement
   - ml_logs : Logs des prédictions de l'API
```

**Équivalent SQL manuel** :

```sql
-- Création de la base
CREATE DATABASE oc_p5_db;
CREATE USER ml_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE oc_p5_db TO ml_user;

-- Connexion et création des tables
\c oc_p5_db

CREATE TABLE dataset (
    id SERIAL PRIMARY KEY,
    features_json JSON NOT NULL,
    target VARCHAR(10) NOT NULL
);

CREATE TABLE ml_logs (
    id SERIAL PRIMARY KEY,
    input_json JSON NOT NULL,
    prediction VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Insertion des Données d'Entraînement

**Script** : `scripts/insert_dataset.py`

```bash
# Fusionne les 3 CSV et insère dans PostgreSQL
python scripts/insert_dataset.py
```

**Fichiers sources** :
- `data/extrait_sondage.csv` (satisfaction employés)
- `data/extrait_eval.csv` (évaluations performance)
- `data/extrait_sirh.csv` (données RH administratives)

**Résultat** : 1470 employés insérés dans `dataset`

---

## Structure des Tables

### Table `dataset`

Stocke les données d'entraînement du modèle ML.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | SERIAL (PK) | Identifiant unique auto-incrémenté |
| `features_json` | JSON | Toutes les caractéristiques de l'employé (âge, salaire, satisfaction, etc.) |
| `target` | VARCHAR(10) | Résultat attendu : 'Oui' (quittera) ou 'Non' (restera) |

**Exemple d'enregistrement** :

```json
{
  "id": 1,
  "features_json": {
    "age": 35,
    "genre": "Homme",
    "revenu_mensuel": 4500,
    "departement": "Commercial",
    "satisfaction_employee_environnement": 3,
    "...": "..."
  },
  "target": "Non"
}
```

### Table `ml_logs`

Logs de traçabilité des prédictions API (étape 6).

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | SERIAL (PK) | Identifiant unique auto-incrémenté |
| `input_json` | JSON | Données envoyées au modèle lors de la prédiction |
| `prediction` | VARCHAR(10) | Résultat de la prédiction ('Oui' ou 'Non') |
| `created_at` | TIMESTAMP | Date/heure de la prédiction (automatique) |

**Exemple d'enregistrement** :

```json
{
  "id": 42,
  "input_json": {
    "age": 28,
    "revenu_mensuel": 3200,
    "departement": "RH",
    "...": "..."
  },
  "prediction": "Oui",
  "created_at": "2026-01-11 17:30:45"
}
```

---

## Requêtes SQL Utiles

### Connexion à la Base

```bash
# Ligne de commande
psql -h localhost -U ml_user -d oc_p5_db
```

### Opérations de Base

```sql
-- Lister les tables
\dt

-- Structure d'une table
\d dataset
\d ml_logs

-- Compter les enregistrements
SELECT COUNT(*) FROM dataset;
SELECT COUNT(*) FROM ml_logs;

-- Exemples de données
SELECT * FROM dataset LIMIT 5;
SELECT * FROM ml_logs ORDER BY created_at DESC LIMIT 10;
```

### Requêtes Analytiques

```sql
-- Distribution des prédictions (turnover)
SELECT target, COUNT(*) as nombre
FROM dataset
GROUP BY target;

-- Prédictions récentes (dernières 24h)
SELECT COUNT(*) FROM ml_logs 
WHERE created_at > NOW() - INTERVAL '1 day';

-- Statistiques par département
SELECT 
    features_json->>'departement' as dept,
    COUNT(*) as total,
    SUM(CASE WHEN target = 'Oui' THEN 1 ELSE 0 END) as departs
FROM dataset
GROUP BY features_json->>'departement';

-- Recherche par critère (ex: âge)
SELECT * FROM dataset 
WHERE (features_json->>'age')::int > 50;
```

---

## Sauvegarde et Restauration

### Sauvegarde

```bash
# Export complet de la base
pg_dump -h localhost -U ml_user -d oc_p5_db -F c -f backup_oc_p5.dump

# Export SQL texte
pg_dump -h localhost -U ml_user -d oc_p5_db > backup_oc_p5.sql

# Export d'une seule table
pg_dump -h localhost -U ml_user -d oc_p5_db -t dataset > dataset_backup.sql
```

### Restauration

```bash
# Depuis un dump binaire
pg_restore -h localhost -U ml_user -d oc_p5_db backup_oc_p5.dump

# Depuis un fichier SQL
psql -h localhost -U ml_user -d oc_p5_db < backup_oc_p5.sql
```

---

## ORM SQLAlchemy

Le projet utilise **SQLAlchemy** pour interagir avec PostgreSQL via Python.

**Modèles définis** : `db_models.py`

```python
from db_models import Dataset, MLLog
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import get_settings

# Configuration
settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Exemple : Lire toutes les données d'entraînement
datasets = session.query(Dataset).all()
for data in datasets[:5]:
    print(f"ID: {data.id}, Target: {data.target}")

# Exemple : Insérer un log de prédiction
log = MLLog(
    input_json={"age": 30, "revenu_mensuel": 3500},
    prediction="Non"
)
session.add(log)
session.commit()

# Fermer la session
session.close()
```

---

## Outils Graphiques (Optionnel)

### DBeaver

Interface graphique pour visualiser et gérer PostgreSQL.

```bash
# Installation (Ubuntu/Linux)
sudo snap install dbeaver-ce

# Configuration
# Host: localhost
# Port: 5432
# Database: oc_p5_db
# User: ml_user
```

### pgAdmin

Alternative plus complète :

```bash
# Installation
sudo apt install pgadmin4
```

---

## Troubleshooting

### Erreur : "password authentication failed"

Vérifier le fichier `.env` et la variable `DATABASE_URL`.

### Erreur : "database does not exist"

Créer manuellement :
```bash
psql -U postgres
CREATE DATABASE oc_p5_db;
```

### Logs PostgreSQL

```bash
# Ubuntu/Debian
sudo tail -f /var/log/postgresql/postgresql-*.log
```
