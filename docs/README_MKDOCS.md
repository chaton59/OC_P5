# Site de Documentation MkDocs

Ce projet utilise **MkDocs** avec le thème **Material** pour générer un site de documentation statique professionnel.

## 🌐 Aperçu

Le site de documentation compile automatiquement tous les fichiers Markdown du dossier `docs/` en un site HTML navigable avec :

- ✅ **Thème Material** moderne et responsive
- ✅ **Navigation par onglets** avec sidebar
- ✅ **Recherche intégrée** (français)
- ✅ **Syntax highlighting** pour code
- ✅ **Mode sombre/clair** automatique
- ✅ **Admonitions** (notes, warnings, tips)
- ✅ **Tabs de contenu** (exemples multi-langages)
- ✅ **Minification** HTML/CSS/JS

## 📦 Installation

Les dépendances MkDocs sont déjà dans `pyproject.toml` (groupe dev) :

```bash
poetry install  # Installe tout, incluant MkDocs
```

## 🚀 Utilisation

### Build du site

Génère le site statique dans `site/` :

```bash
poetry run mkdocs build
```

**Sortie** : `site/index.html` + tous les fichiers HTML

### Preview local

Lance un serveur de développement avec rechargement automatique :

```bash
poetry run mkdocs serve
```

**Accès** : http://127.0.0.1:8000

Modifications dans `docs/` → Rechargement automatique du navigateur

### Déploiement

#### Option 1 : GitHub Pages (recommandé)

```bash
poetry run mkdocs gh-deploy
```

Déploie automatiquement sur `https://username.github.io/OC_P5/`

#### Option 2 : Serveur statique

Copier le dossier `site/` vers votre serveur web (Nginx, Apache, etc.)

```bash
# Exemple avec rsync
rsync -avz site/ user@server:/var/www/docs/
```

## 📁 Structure

```
docs/
├── index.md                  # Page d'accueil
├── installation.md           # Guide d'installation
├── configuration.md          # Configuration
├── quickstart.md             # Démarrage rapide
├── changelog.md              # Historique versions
│
├── api/
│   └── guide.md              # Guide API condensé
│
├── model/
│   └── technical.md          # Doc technique modèle
│
├── API_GUIDE.md              # Doc API complète (981 lignes)
├── MODEL_TECHNICAL.md        # Doc modèle complète (393 lignes)
├── TRAINING.md               # Guide d'entraînement
├── DEPLOYMENT.md             # Guide de déploiement
├── database_guide.md         # Guide BDD
└── DOCUMENTATION_INVENTORY.md # Inventaire docs

mkdocs.yml                    # Configuration MkDocs
```

## ⚙️ Configuration

### mkdocs.yml

Fichier de configuration principal :

- **Theme** : Material avec palette light/dark
- **Extensions** : Admonitions, code highlighting, tables, etc.
- **Plugins** : Search (français), minify
- **Navigation** : Structure hiérarchique des pages

### Personnalisation

**Modifier le thème** :

```yaml
theme:
  palette:
    primary: indigo  # Couleur primaire
    accent: blue     # Couleur d'accent
```

**Ajouter des pages** :

```yaml
nav:
  - Nouvelle Section:
    - Ma Page: path/to/page.md
```

## 🎨 Extensions Markdown

### Admonitions (notes colorées)

```markdown
!!! note "Titre optionnel"
    Contenu de la note

!!! warning
    Attention !

!!! tip
    Astuce utile

!!! success
    Opération réussie
```

### Tabs de contenu

```markdown
=== "Python"
    ```python
    print("Hello")
    ```

=== "JavaScript"
    ```javascript
    console.log("Hello");
    ```
```

### Code avec numéros de lignes

```markdown
​```python linenums="1"
def hello():
    print("World")
​```
```

### Liens et références

```markdown
[Lien vers autre page](api/guide.md)
[Lien externe](https://example.com)
```

## 🔍 Recherche

La recherche fonctionne automatiquement avec le plugin `search` :

- Indexation de tout le contenu Markdown
- Support français (stemming, stop words)
- Suggestions au fil de la frappe
- Highlight des résultats

## 📊 Métriques

### Temps de build

```bash
time poetry run mkdocs build
# Documentation built in 0.70 seconds
```

### Taille du site

```bash
du -sh site/
# ~3.5 MB (incluant assets Material theme)
```

### Pages générées

- **9 pages personnalisées** (index, installation, config, etc.)
- **8 pages de documentation existante** (API_GUIDE, MODEL_TECHNICAL, etc.)
- **Total : 17 pages HTML**

## 🛠️ Maintenance

### Mettre à jour MkDocs

```bash
poetry update mkdocs mkdocs-material
```

### Ajouter un plugin

```bash
poetry add --group dev mkdocs-plugin-name
```

Puis dans `mkdocs.yml` :

```yaml
plugins:
  - search
  - plugin-name
```

### Vérifier les liens cassés

```bash
poetry run mkdocs build --strict
```

Mode strict : erreur si lien invalide détecté.

## 🚨 Troubleshooting

### "Plugin not installed"

**Solution** :

```bash
poetry install  # Réinstaller toutes les dépendances
```

### Lien cassé vers fichier

**Vérifier** :
- Le fichier existe dans `docs/`
- Le chemin est relatif (pas de `docs/` dans le lien)
- Extension `.md` incluse

### Thème ne s'affiche pas

**Vérifier** :

```bash
poetry show mkdocs-material
# Doit afficher : mkdocs-material 9.7.1
```

## 📚 Ressources

- **MkDocs** : https://www.mkdocs.org
- **Material Theme** : https://squidfunk.github.io/mkdocs-material/
- **Extensions Markdown** : https://squidfunk.github.io/mkdocs-material/reference/

## 📝 Notes

### Pourquoi MkDocs ?

Comme recommandé dans `etapes.txt` :

> "MkDocs pour accessibilité (HTML interactif)"

**Avantages** :
- Site professionnel sans effort
- Recherche intégrée
- Navigation claire
- Mobile-friendly
- Versioning facile

### Alternative : Markdown pur

Pour un POC simple, les fichiers Markdown existants suffisent. MkDocs est **optionnel** mais améliore grandement l'expérience utilisateur pour une documentation complexe.

---

**Généré par** : OpenClassrooms P5 - Étape 6 (Documentation)  
**Date** : Janvier 2026  
**Version** : 1.0.0
