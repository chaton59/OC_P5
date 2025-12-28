# 🗄️ Guide Débutant - Base de Données PostgreSQL

## 📋 Vue d'ensemble

Notre projet utilise **PostgreSQL** comme base de données pour stocker :
- Les données d'entraînement du modèle (`dataset`)
- Les logs des prédictions (`ml_logs`)

## 🛠️ Outils nécessaires

### 1. psql (Client PostgreSQL)
Déjà installé sur votre système Ubuntu.

### 2. DBeaver (Interface graphique - Optionnel)
Pour une visualisation plus facile :
```bash
# Installation
sudo snap install dbeaver-ce
```

## 🔗 Connexion à la base de données

### Informations de connexion :
- **Hôte** : `localhost` (ou `127.0.0.1`)
- **Port** : `5432`
- **Base** : `oc_p5_db`
- **Utilisateur** : `ml_user`
- **Mot de passe** : `15975359320`

### Commande de connexion :
```bash
psql -h localhost -U ml_user -d oc_p5_db
```

## 📊 Structure des tables

### Table `dataset`
Stocke les données d'entraînement du modèle.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INTEGER | Identifiant unique (clé primaire) |
| `features_json` | JSON | Toutes les caractéristiques (âge, salaire, etc.) |
| `target` | STRING | Résultat attendu ('Oui' = quittera, 'Non' = restera) |

### Table `ml_logs`
Stocke les logs des prédictions de l'API.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INTEGER | Identifiant unique (clé primaire) |
| `input_json` | JSON | Données envoyées au modèle |
| `prediction` | STRING | Prédiction du modèle ('Oui'/'Non') |
| `created_at` | DATETIME | Date/heure de la prédiction |

## 🔍 Requêtes de base

### Se connecter :
```bash
psql -h localhost -U ml_user -d oc_p5_db
# Mot de passe : 15975359320
```

### Lister les tables :
```sql
\dt
```

### Voir la structure d'une table :
```sql
\d dataset
\d ml_logs
```

### Compter les enregistrements :
```sql
SELECT COUNT(*) FROM dataset;
SELECT COUNT(*) FROM ml_logs;
```

### Voir tous les enregistrements :
```sql
SELECT * FROM dataset LIMIT 5;
SELECT * FROM ml_logs LIMIT 5;
```

### Voir les prédictions récentes :
```sql
SELECT * FROM ml_logs ORDER BY created_at DESC LIMIT 10;
```

### Voir les données d'un employé spécifique :
```sql
SELECT * FROM dataset WHERE features_json->>'age' = '35';
```

### Statistiques des prédictions :
```sql
SELECT prediction, COUNT(*) as nombre
FROM ml_logs
GROUP BY prediction;
```

## 📈 Exemples pratiques

### 1. Voir les données d'entraînement :
```sql
SELECT
    id,
    features_json->>'age' as age,
    features_json->>'genre' as genre,
    features_json->>'revenu_mensuel' as salaire,
    target
FROM dataset
LIMIT 10;
```

### 2. Voir les logs des dernières heures :
```sql
SELECT
    created_at,
    prediction,
    input_json->>'age' as age_client
FROM ml_logs
WHERE created_at >= NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

### 3. Analyser les prédictions par âge :
```sql
SELECT
    CASE
        WHEN (input_json->>'age')::int < 30 THEN '< 30 ans'
        WHEN (input_json->>'age')::int BETWEEN 30 AND 40 THEN '30-40 ans'
        ELSE '> 40 ans'
    END as tranche_age,
    prediction,
    COUNT(*) as nombre
FROM ml_logs
GROUP BY tranche_age, prediction
ORDER BY tranche_age, prediction;
```

## 🎯 Intégration avec l'API

### Comment ça fonctionne :
1. **Prédiction** : L'API reçoit des données → Modèle prédit → Résultat stocké dans `ml_logs`
2. **Traçabilité** : Toutes les prédictions sont enregistrées avec date/heure
3. **Audit** : On peut voir l'historique complet des utilisations

### Exemple de workflow :
```python
# Dans l'API FastAPI
from sqlalchemy.orm import sessionmaker
from models import MLLog

# Après prédiction
log_entry = MLLog(
    input_json=input_data,
    prediction=result
)
session.add(log_entry)
session.commit()
```

## 🖥️ Interface graphique (DBeaver)

### Configuration de connexion :
1. Ouvrir DBeaver
2. **Nouvelle connexion** → PostgreSQL
3. **Hôte** : `localhost`
4. **Port** : `5432`
5. **Base** : `oc_p5_db`
6. **Utilisateur** : `ml_user`
7. **Mot de passe** : `15975359320`
8. **Tester la connexion** → **Terminer**

### Navigation :
- **Tables** : Voir la structure et les données
- **SQL Editor** : Écrire vos propres requêtes
- **Export** : Sauvegarder les résultats en CSV

## 🔧 Commandes utiles

### Sauvegarder la base :
```bash
pg_dump -h localhost -U ml_user -d oc_p5_db > backup.sql
```

### Restaurer la base :
```bash
psql -h localhost -U ml_user -d oc_p5_db < backup.sql
```

### Quitter psql :
```sql
\q
```

## 📚 Ressources pour aller plus loin

- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
- [Tutoriel SQL pour débutants](https://sqlzoo.net/)
- [DBeaver Documentation](https://dbeaver.com/docs/)

## ❓ Dépannage

### Problème : "Password authentication failed"
**Solution** : Vérifier le mot de passe (`15975359320`)

### Problème : "Connection refused"
**Solution** : Vérifier que PostgreSQL tourne (`sudo systemctl status postgresql`)

### Problème : "Table does not exist"
**Solution** : Les tables sont créées automatiquement par SQLAlchemy lors du premier test