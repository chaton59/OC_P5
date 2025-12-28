# 📁 Scripts Utilitaires

Ce dossier contient tous les scripts utilitaires pour la gestion de l'application.

## 📋 Scripts disponibles

### 🗄️ `insert_dataset.py`
**Rôle** : Insère le dataset complet dans PostgreSQL
```bash
poetry run python scripts/insert_dataset.py
```
- Charge les 3 fichiers CSV (sondage, eval, sirh)
- Fusionne les données selon les clés communes
- Insère 1470 employés dans la table `dataset`

### 🧪 `test_db.py`
**Rôle** : Teste la connexion et les opérations de base de données
```bash
poetry run python scripts/test_db.py
```
- Vérifie la connexion PostgreSQL
- Crée les tables si nécessaire
- Insère des données de test
- Valide le fonctionnement du schéma

### 🚀 `run_local.sh`
**Rôle** : Script de lancement local pour développement
```bash
bash scripts/run_local.sh
```
- Lance l'API FastAPI en mode développement
- Configure les variables d'environnement
- Active le rechargement automatique

## 📁 Organisation

```
scripts/
├── insert_dataset.py    # Gestion des données
├── test_db.py          # Tests base de données
└── run_local.sh        # Lancement local
```

## 🔧 Utilisation

Tous les scripts utilisent Poetry pour la gestion des dépendances :
```bash
poetry run python scripts/<nom_script>.py
```

## 📚 Documentation

Voir le guide complet : [docs/database_guide.md](../docs/database_guide.md)