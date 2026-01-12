# Guide de déploiement rapide sur HuggingFace Spaces

## ✅ Prérequis

Votre application est maintenant configurée pour déployer **FastAPI + Gradio** ensemble.

## 🚀 Déploiement en 3 étapes

### Étape 1 : Tester localement

```bash
# Lancer le script de test
./test_deployment.sh
```

Si tous les tests passent ✅, passez à l'étape 2.

### Étape 2 : Commiter les changements

```bash
# Voir les fichiers modifiés
git status

# Ajouter tous les fichiers
git add app.py src/Dockerfile HF_DEPLOYMENT.md test_deployment.sh QUICK_DEPLOY.md

# Commiter
git commit -m "Deploy: FastAPI + Gradio on HuggingFace Spaces"

# Pousser sur GitHub
git push origin main
```

### Étape 3 : Synchroniser HuggingFace Spaces

HuggingFace Spaces se synchronise automatiquement avec votre repo GitHub.

1. Allez sur https://huggingface.co/spaces/votre-username/votre-space
2. Cliquez sur l'onglet **"Settings"**
3. Dans "Repository", vérifiez que le lien GitHub est configuré
4. Le Space va se rebuilder automatiquement
5. Vérifiez les logs dans l'onglet **"Logs"**

## 📋 Checklist de vérification

- [ ] Les tests locaux passent (`./test_deployment.sh`)
- [ ] Le fichier `README.md` contient le header YAML avec `sdk: gradio`
- [ ] Les dépendances sont à jour dans `pyproject.toml`
- [ ] Les secrets sont configurés sur HF Spaces (API_KEY, DEBUG, etc.)
- [ ] Le repository GitHub est synchronisé

## 🔍 Vérification après déploiement

Une fois le Space déployé, vérifiez :

1. **Interface Gradio** : Accédez à `https://votre-space.hf.space/`
   - Testez une prédiction unitaire
   - Testez une prédiction batch

2. **Logs** : Consultez les logs sur HF Spaces
   ```
   ✅ Recherchez ces messages :
   - "🚀 Démarrage de l'application complète"
   - "[FastAPI] Application startup complete"
   - "✅ FastAPI démarré et opérationnel"
   - "🌐 Lancement du serveur sur 0.0.0.0:7860"
   ```

3. **API interne** : L'API FastAPI tourne en interne (non accessible publiquement)

## ⚠️ Problèmes courants

### Le Space ne démarre pas

**Symptômes** : Le Space affiche "Building" indéfiniment ou erreur au démarrage

**Solutions** :
1. Vérifiez les logs HF Spaces
2. Vérifiez que `pyproject.toml` et `poetry.lock` sont synchronisés
3. Vérifiez que toutes les dépendances sont installables
4. Essayez de rebuilder manuellement : Settings → Factory reboot

### FastAPI ne démarre pas

**Symptômes** : Dans les logs, erreur au démarrage de uvicorn

**Solutions** :
1. Vérifiez que `uvicorn` est dans `pyproject.toml`
2. Vérifiez que `api.py` est bien copié (voir `src/Dockerfile`)
3. Vérifiez que le modèle est téléchargeable depuis HF Hub

### Gradio ne répond pas

**Symptômes** : "502 Bad Gateway" ou page blanche

**Solutions** :
1. Vérifiez que `sdk: gradio` est dans le header YAML du README
2. Vérifiez que `app_file: app.py` pointe vers le bon fichier
3. Attendez 2-3 minutes (le premier démarrage est long)

### "API not found" dans l'interface

**Symptômes** : L'interface s'affiche mais les prédictions échouent

**Solutions** :
1. Vérifiez que FastAPI a bien démarré (logs)
2. Vérifiez que le port 8000 n'est pas bloqué
3. Augmentez le temps d'attente dans `app.py` (ligne avec `sleep(5)`)

## 🔄 Mise à jour du Space

Pour mettre à jour votre Space après modification :

```bash
# 1. Modifier vos fichiers
# 2. Commiter
git add .
git commit -m "Update: description des changements"
git push origin main

# 3. HF Spaces se met à jour automatiquement (1-2 minutes)
```

## 📞 Support

- Documentation HF : https://huggingface.co/docs/hub/spaces
- Documentation Gradio : https://gradio.app/docs/
- Documentation FastAPI : https://fastapi.tiangolo.com/

## 🎉 Vous êtes prêt !

Votre application est maintenant prête à être déployée avec :
- ✅ API REST complète (FastAPI)
- ✅ Interface web interactive (Gradio)
- ✅ Prédictions unitaires et batch
- ✅ Documentation automatique
- ✅ Monitoring et logs

Bon déploiement ! 🚀
