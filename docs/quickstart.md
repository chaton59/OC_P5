# Premier Déploiement

Guide rapide pour déployer l'API en 10 minutes.

## Prérequis

- [x] Compte GitHub
- [x] Compte HuggingFace (gratuit)
- [x] Repository cloné localement
- [x] Python 3.12+ installé

---

## Étape 1 : Configuration Locale (2 min)

### Installer les dépendances

```bash
cd OC_P5
poetry install
```

### Créer le fichier .env

```bash
cp .env.example .env
```

Éditer `.env` :

```bash
DEBUG=true
LOG_LEVEL=INFO
```

---

## Étape 2 : Tester en Local (3 min)

### Lancer l'API

```bash
poetry run uvicorn api:app --reload
```

### Tester le health check

```bash
curl http://localhost:8000/health
```

**Réponse attendue** :

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "3.2.1"
}
```

### Tester une prédiction

Ouvrir http://localhost:8000/docs et utiliser l'interface Swagger pour tester `/predict`.

---

## Étape 3 : Créer un Space HuggingFace (5 min)

### Créer un nouveau Space

1. Aller sur https://huggingface.co/spaces
2. Cliquer sur **"Create new Space"**
3. Remplir :
   - **Space name** : `oc_p5` (ou autre nom)
   - **License** : MIT
   - **SDK** : Docker
   - **Visibility** : Public ou Private

### Configurer les secrets

Dans les settings du Space, ajouter :

```
API_KEY=votre-clé-secrète-générée
DEBUG=false
LOG_LEVEL=INFO
```

### Lier au repository GitHub

Dans les settings du Space :
1. Aller dans **"Settings" → "Repository"**
2. Cliquer sur **"Link to GitHub"**
3. Sélectionner votre repo `OC_P5`
4. Sélectionner la branche `main`

---

## Étape 4 : Déploiement Automatique

### Push vers GitHub

```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

### Vérifier le déploiement

GitHub Actions va automatiquement :
1. Linter le code (Black + Flake8)
2. Exécuter les tests (97 tests)
3. Déployer sur HuggingFace Spaces

**Temps total** : ~5-7 minutes

### Accéder à l'API déployée

URL : `https://your-username-oc-p5.hf.space`

Tester :

```bash
curl https://your-username-oc-p5.hf.space/health
```

---

## Étape 5 : Environnement de Développement (Optionnel)

### Créer un Space dev

Répéter les étapes ci-dessus avec :
- **Space name** : `oc_p5-dev`
- **Branche GitHub** : `dev`
- **DEBUG** : `true` (pas d'auth requise)

### Workflow de développement

```bash
# Développement sur branche dev
git checkout dev
# ... faire des modifications ...
git commit -am "Feature X"
git push origin dev  # Déploie automatiquement sur oc_p5-dev

# Validation OK → Merge vers main
git checkout main
git merge dev
git push origin main  # Déploie sur oc_p5 (production)
```

---

## 🎉 Félicitations !

Votre API est maintenant déployée et accessible publiquement !

### Prochaines étapes

- [x] API fonctionnelle en production
- [ ] Configurer le monitoring (logs HF Spaces)
- [ ] Tester les endpoints avec des données réelles
- [ ] Partager l'URL avec votre équipe

### Liens utiles

- **API Production** : `https://your-username-oc-p5.hf.space`
- **Swagger** : `https://your-username-oc-p5.hf.space/docs`
- **GitHub Actions** : `https://github.com/your-username/OC_P5/actions`

---

## Troubleshooting

### L'API ne démarre pas sur HF Spaces

**Vérifier** :
1. Les logs du Space (onglet "Logs")
2. Que `Dockerfile` et `requirements.txt` sont à jour
3. Que les secrets sont bien configurés

### GitHub Actions échoue

**Causes communes** :
- Tests qui échouent localement → `poetry run pytest`
- Linter qui échoue → `poetry run black . --check`
- Token HF invalide → Vérifier le secret `HF_TOKEN`

### Erreur 401 sur `/predict`

**Solution** :
- Ajouter le header `X-API-Key` avec la valeur du secret
- Ou mettre `DEBUG=true` pour désactiver l'auth (dev uniquement)

---

## 📞 Support

- **Issues GitHub** : [github.com/chaton59/OC_P5/issues](https://github.com/chaton59/OC_P5/issues)
- **Documentation complète** : [Déploiement avancé](deployment/overview.md)
