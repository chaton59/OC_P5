# Déploiement sur HuggingFace Spaces

## Architecture déployée

L'application lance **2 services simultanément** :

1. **FastAPI** (port 8000) : API REST complète
2. **Gradio** (port 7860) : Interface web interactive

## URLs d'accès

Sur HuggingFace Spaces, l'application sera accessible à :

- **Interface Gradio** : `https://votre-space.hf.space/` (port public 7860)
- **API FastAPI** : Accessible en interne via `http://localhost:8000`

⚠️ **Note importante** : HuggingFace Spaces n'expose publiquement que le port 7860 (Gradio). L'API FastAPI est accessible uniquement en interne ou via l'interface Gradio.

## Configuration requise sur HF Spaces

### 1. Variables d'environnement (Secrets)

Dans les paramètres de votre Space, configurez ces secrets :

```bash
API_KEY=votre-clé-api-production
DEBUG=false
LOG_LEVEL=INFO
GRADIO_ENABLED=true
```

### 2. Fichiers nécessaires

Ces fichiers doivent être présents dans le repository :

```
.
├── app.py                 # Lance FastAPI + Gradio
├── api.py                 # Code FastAPI
├── db_models.py          # Modèles BDD (optionnel sur HF)
├── pyproject.toml        # Dépendances Poetry
├── poetry.lock           # Lock des versions
├── README.md             # Documentation + metadata HF
└── src/
    ├── __init__.py
    ├── auth.py
    ├── config.py
    ├── gradio_ui.py      # Interface Gradio
    ├── logger.py
    ├── models.py
    ├── preprocessing.py
    ├── rate_limit.py
    └── schemas.py
```

### 3. Metadata HF dans README.md

Assurez-vous que le header YAML dans `README.md` contient :

```yaml
---
title: Employee Turnover Prediction API
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "5.9.1"
app_file: app.py
pinned: false
---
```

## Comment l'application démarre

1. `app.py` démarre FastAPI sur le port 8000 (background)
2. Attend que FastAPI soit opérationnel (health check)
3. Lance Gradio sur le port 7860 (foreground)
4. Les deux services communiquent en interne

## Test local

Pour tester localement avant déploiement :

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer l'application
python app.py
```

Puis accédez à :
- Gradio : http://localhost:7860
- FastAPI : http://localhost:8000/docs

## Utilisation de l'API depuis l'extérieur

### Option 1 : Via l'interface Gradio (recommandé)

Utilisez l'interface web directement sur `https://votre-space.hf.space/`

### Option 2 : Via l'API Gradio (pour scripts externes)

Gradio expose automatiquement une API pour ses fonctions :

```python
from gradio_client import Client

client = Client("https://votre-space.hf.space/")
result = client.predict(
    nombre_participation_pee=0,
    nb_formations_suivies=2,
    # ... autres paramètres
    api_name="/predict"
)
print(result)
```

### Option 3 : FastAPI (uniquement en local ou si proxy configuré)

L'API FastAPI n'est pas directement accessible depuis l'extérieur sur HF Spaces.

## Dépannage

### Le Space ne démarre pas

1. Vérifiez les logs dans l'onglet "Logs" de HF Spaces
2. Vérifiez que `pyproject.toml` et `poetry.lock` sont à jour
3. Vérifiez que toutes les dépendances sont installables

### FastAPI ne démarre pas

- Vérifiez que `uvicorn` est dans les dépendances
- Vérifiez les logs pour les erreurs de port
- Assurez-vous que le modèle est bien téléchargeable depuis HF Hub

### Gradio ne répond pas

- Vérifiez que le port 7860 n'est pas bloqué
- Vérifiez que `sdk: gradio` est bien dans le README
- Vérifiez que `app_file: app.py` pointe vers le bon fichier

## Logs et monitoring

Les logs sont visibles dans l'onglet "Logs" de HF Spaces. Format :

```
2026-01-12 03:22:01,905 - INFO - 🚀 Démarrage de l'application complète
2026-01-12 03:22:02,256 - INFO - [FastAPI] Application startup complete
2026-01-12 03:22:04,855 - INFO - ✅ FastAPI démarré et opérationnel
2026-01-12 03:22:06,717 - INFO - 🌐 Lancement du serveur sur 0.0.0.0:7860...
```

## Mise à jour du déploiement

Pour mettre à jour l'application :

1. Committez vos changements sur GitHub
2. HF Spaces se synchronise automatiquement
3. Le Space redémarre avec les nouveaux fichiers
4. Vérifiez les logs pour confirmer le bon démarrage

## Support

En cas de problème :
1. Consultez les logs HF Spaces
2. Testez localement avec `python app.py`
3. Vérifiez la documentation : https://huggingface.co/docs/hub/spaces
