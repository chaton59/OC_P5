# 🔧 Guide de Dépannage - HuggingFace Spaces

## Erreur : "No module named 'slowapi'"

### Cause
FastAPI n'a pas pu démarrer parce que la dépendance `slowapi` n'a pas été installée lors du build Docker.

### Raisons possibles
1. **Cache de dépendances** - HF Spaces a peut-être mis en cache une ancienne version
2. **Installation incomplète** - Poetry n'a pas installé toutes les dépendances
3. **Timeout lors du build** - Le build a peut-être expiré

### Solutions (dans l'ordre)

#### ✅ **Solution 1 : Factory Reboot (Recommandé)**

1. Allez sur votre HF Space : https://huggingface.co/spaces/votre-username/oc-p5-dev
2. Cliquez sur **Settings** (⚙️)
3. Scrollez jusqu'à **"Reboot"**
4. Cliquez sur **"Factory reboot"**
5. Attendez 3-5 minutes que le Space se reconstruise

Cela efface le cache et force HF à télécharger toutes les dépendances depuis zéro.

#### ✅ **Solution 2 : Vérifier que poetry.lock est à jour**

Localement :
```bash
cd /home/valentin/Env_Python/OC_P5
poetry lock
git add poetry.lock
git commit -m "sync: update poetry.lock"
git push origin main
```

Attendez 2-3 minutes que HF Spaces se synchronise, puis attendez le rebuild.

#### ✅ **Solution 3 : Ajouter une étape de diagnostic dans le Dockerfile**

Le Dockerfile a été mis à jour pour vérifier que les dépendances critiques sont bien installées :

```dockerfile
RUN python -c "import slowapi; import fastapi; import gradio; print('All critical dependencies installed ✓')"
```

Si cette étape échoue, le build Docker échouera immédiatement avec un message clair.

#### ✅ **Solution 4 : Forcer un build sans cache**

Sur HF Spaces :
1. Settings → Advanced settings
2. Cochez l'option "Disable cache" ou similaire
3. Cliquez sur "Restart" ou "Rebuild"

## Symptômes et solutions

### Symptôme : "Error: No API found"

**Signifie** : Gradio démarre mais FastAPI n'a pas pu démarrer.

**Solution** :
1. Vérifiez les logs HF Spaces
2. Recherchez "ModuleNotFoundError: No module named 'slowapi'"
3. Si oui, appliquez "Solution 1" (Factory reboot)

### Symptôme : "502 Bad Gateway"

**Signifie** : Gradio n'a pas pu démarrer ou le port 7860 est occupé.

**Solution** :
1. Attendez 2-3 minutes (premier démarrage peut être lent)
2. Appliquez "Solution 1" (Factory reboot)
3. Vérifiez les logs pour les erreurs Gradio

### Symptôme : "Connection refused" sur le health check

**Signifie** : FastAPI a crashé après son démarrage.

**Solution** :
1. Cherchez "Traceback" dans les logs
2. Identifiez l'erreur Python
3. Corrigez le code et poussez une nouvelle version

## Vérification locale

Avant de déployer, testez toujours localement :

```bash
# Lancer le test complet
./test_deployment.sh

# Ou tester individuellement
poetry run uvicorn api:app --host 0.0.0.0 --port 8000 &
python app.py
```

## Fichiers importants

- `pyproject.toml` - Déclare toutes les dépendances
- `poetry.lock` - Versions exactes des dépendances (DOIT être synchronisé)
- `src/Dockerfile` - Build image pour HF Spaces
- `app.py` - Lance FastAPI + Gradio

## Logs à surveiller

Sur HF Spaces, dans l'onglet "Logs", recherchez ces patterns :

```
✓ "[FastAPI] Application startup complete" - FastAPI a démarré
✓ "Running on local URL: http://0.0.0.0:7860" - Gradio a démarré
✗ "ModuleNotFoundError: No module named 'slowapi'" - Dépendance manquante
✗ "Traceback" - Erreur Python
```

## Points clés

- `slowapi` est une dépendance de **production** (en development dependencies)
- `poetry.lock` DOIT être à jour (généré avec `poetry lock`)
- HF Spaces peut mettre en cache → utiliser Factory reboot si nécessaire
- Le premier build peut prendre 5-10 minutes

## Questions fréquentes

**Q : Pourquoi ça fonctionne en local mais pas sur HF ?**
A : Probablement un problème d'installation des dépendances lors du build Docker. Utilisez Factory reboot.

**Q : Combien de temps ça prend à déployer ?**
A : Généralement 3-10 minutes après un push sur GitHub.

**Q : Pourquoi je vois "API not found" ?**
A : FastAPI n'a pas démarré. Vérifiez les logs pour "ModuleNotFoundError" ou "Traceback".

## Contact & Support

- Documentation HF : https://huggingface.co/docs/hub/spaces
- Documentation Gradio : https://gradio.app/docs/
- Documentation FastAPI : https://fastapi.tiangolo.com/
