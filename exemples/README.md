# 🚀 DÉMONSTRATION API Employee Turnover

**Par défaut** : API locale `http://127.0.0.1:7860`  
**Production** : Hugging Face Spaces `https://asi-engineer-oc-p5.hf.space`

## ⚙️ Configuration

Les scripts locaux utilisent par défaut l'API locale. Pour la Space Hugging Face, des scripts dédiés sont fournis et acceptent `HF_API_URL` comme variable d'environnement.

## 📋 Installation

```bash
pip install requests pandas
```

## 🚀 Lancer l'API locale

**Option 1** : Script automatique
```bash
./lancer_api.sh
```

**Option 2** : Commande manuelle
```bash
cd ..  # Retour au dossier racine
poetry run uvicorn api:app --host 127.0.0.1 --port 7860
```

L'API sera disponible sur `http://127.0.0.1:7860`

## 🔮 Prédiction UNITAIRE (1 employé)

**Usage ultra-simple** : Le script pose toutes les questions une par une.

```bash
python demo_unitaire.py
```

Le script demande les informations de l'employé, interroge l'API et affiche le résultat immédiatement.

**Exemple de sortie** :
```
📊 RÉSULTAT
══════════════════════════════════════════════════════════
✅ PRÉDICTION: L'EMPLOYÉ VA RESTER
🎯 Niveau de risque: Low
   Probabilité de rester: 85.2%
   Probabilité de partir: 14.8%
```

---

## 📦 Prédiction BATCH (fichiers CSV)

**Usage ultra-simple** : Fournit 3 fichiers CSV, obtient 1 CSV de résultats.

```bash
python demo_batch.py
```

Le script demande les chemins des 3 fichiers CSV :
1. Fichier sondage
2. Fichier évaluation  
3. Fichier SIRH

**Il génère automatiquement** : `predictions_batch_YYYYMMDD_HHMMSS.csv` dans le dossier courant.

**Exemple de sortie** :
```
📊 RÉSUMÉ
══════════════════════════════════════════════════════════
✅ Employés qui vont RESTER: 8
🏃 Employés qui vont PARTIR: 2
🔴 Risque ÉLEVÉ: 1
🟡 Risque MOYEN: 2
🟢 Risque FAIBLE: 7

💾 Résultats sauvegardés dans: predictions_batch_20260111_234530.csv
```

---

## ☁️ Utiliser l'API Hugging Face (Space)

Deux scripts ciblent directement la Space HF:

```bash
python demo_unitaire_hf.py
python demo_batch_hf.py
```

Optionnel: surcharger l'URL via `HF_API_URL`:

```bash
HF_API_URL="https://asi-engineer-oc-p5.hf.space" python demo_batch_hf.py
```

Optionnel: si la Space protège les endpoints, ajouter une API key:

```bash
HF_API_KEY="votre-cle" python demo_unitaire_hf.py
HF_API_KEY="votre-cle" python demo_batch_hf.py
```

Note: si la Space n'expose pas FastAPI, le script batch basculera automatiquement sur l'API Gradio (`/api/predict_batch`) si l'onglet Batch est activé. Sinon, utilisez l'API locale avec `lancer_api.sh`.

---

## 📂 Fichiers d'exemple fournis

Pour tester rapidement, 4 fichiers d'exemple sont fournis :

- **`01_predict_single_employee.json`** - Exemple d'employé pour test unitaire
- **`02_predict_batch_sondage.csv`** - 10 employés (données sondage)
- **`02_predict_batch_eval.csv`** - 10 employés (données évaluation)
- **`02_predict_batch_sirh.csv`** - 10 employés (données SIRH)

**Utilisation** : Indiquez simplement ces chemins quand `demo_batch.py` vous les demande.

---

## 🎯 Jour J - Checklist

1. ✅ Installer les dépendances : `pip install requests pandas`
2. ✅ Tester unitaire : `python demo_unitaire.py`
3. ✅ Tester batch : `python demo_batch.py` (utiliser les fichiers `02_predict_batch_*.csv`)
4. ✅ Vérifier que les CSV de résultats sont générés

**C'est tout !** 🎉

---

## 📖 Documentation complète

Pour plus d'informations sur l'API, les formats de données, etc., voir :
- [API Documentation](../docs/api_documentation.md)
- [Architecture](../docs/architecture.md)

