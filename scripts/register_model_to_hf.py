#!/usr/bin/env python3
"""
Script pour enregistrer le modèle MLflow dans Hugging Face Hub.

Usage:
    python scripts/register_model_to_hf.py

Prérequis:
    - HF_TOKEN configuré dans l'environnement ou .env
    - Modèle entraîné dans MLflow
"""
import os
import mlflow
import mlflow.sklearn
from huggingface_hub import HfApi, login
from pathlib import Path
import shutil


def register_model_to_hf(
    run_id: str,
    hf_repo_id: str = "ASI-Engineer/employee-turnover-model",
    model_name: str = "Employee_Turnover_XGBoost",
):
    """
    Enregistre le modèle MLflow dans le Model Registry puis l'exporte vers HF Hub.

    Args:
        run_id: ID du run MLflow contenant le meilleur modèle
        hf_repo_id: Repository Hugging Face (format: username/repo-name)
        model_name: Nom du modèle dans MLflow Model Registry
    """
    print("=" * 80)
    print("🚀 ENREGISTREMENT DU MODÈLE DANS HUGGING FACE HUB")
    print("=" * 80)
    print()

    # Configuration MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")

    # 1. Enregistrer dans MLflow Model Registry
    print("📦 Étape 1: Enregistrement dans MLflow Model Registry...")
    model_uri = f"runs:/{run_id}/model"

    try:
        # Créer ou mettre à jour le modèle dans le registry
        model_version = mlflow.register_model(model_uri, model_name)
        print(f"   ✅ Modèle enregistré: {model_name} version {model_version.version}")
        print(f"   📍 Run ID: {run_id}")
    except Exception as e:
        print(f"   ℹ️  Modèle déjà enregistré ou erreur: {e}")
        model_version = None

    print()

    # 2. Charger le modèle
    print("📥 Étape 2: Chargement du modèle depuis MLflow...")
    model = mlflow.sklearn.load_model(model_uri)
    print(f"   ✅ Modèle chargé: {type(model).__name__}")
    print()

    # 3. Exporter vers dossier temporaire
    print("💾 Étape 3: Export du modèle...")
    export_dir = Path("./model_export")
    export_dir.mkdir(exist_ok=True)

    # Sauvegarder le modèle au format MLflow
    mlflow.sklearn.save_model(model, str(export_dir / "model"))

    # Créer un README pour HF
    readme_content = f"""---
tags:
- employee-turnover
- xgboost
- mlflow
- classification
library_name: scikit-learn
---

# Employee Turnover Prediction Model

Modèle XGBoost pour prédire le turnover des employés.

## Métriques
- **F1-Score**: Optimisé pour classes déséquilibrées
- **Algorithme**: XGBoost avec SMOTE
- **MLflow Run ID**: `{run_id}`

## Utilisation

```python
import mlflow

# Charger depuis Hugging Face Hub
model = mlflow.sklearn.load_model("hf://{hf_repo_id}")

# Prédiction
predictions = model.predict(X)
```

## Preprocessing
Les artifacts de preprocessing (scaler, encoders) sont disponibles dans MLflow.

## Repository
[GitHub - OC_P5](https://github.com/chaton59/OC_P5)
"""

    with open(export_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"   ✅ Modèle exporté vers: {export_dir}")
    print()

    # 4. Upload vers Hugging Face Hub
    print("☁️  Étape 4: Upload vers Hugging Face Hub...")

    # Login HF (utilise HF_TOKEN depuis env)
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("   ⚠️  HF_TOKEN non trouvé dans l'environnement")
        print(
            "   💡 Conseil: Créez un token sur https://huggingface.co/settings/tokens"
        )
        print("   💡 Puis: export HF_TOKEN='your_token_here'")
        return False

    try:
        login(token=hf_token, add_to_git_credential=False)
        print("   ✅ Authentification Hugging Face réussie")

        # Upload
        api = HfApi()
        api.create_repo(
            repo_id=hf_repo_id, repo_type="model", exist_ok=True, private=False
        )

        api.upload_folder(
            repo_id=hf_repo_id,
            folder_path=str(export_dir),
            repo_type="model",
        )

        print(f"   ✅ Modèle uploadé vers: https://huggingface.co/{hf_repo_id}")
        print()

        # Nettoyage
        shutil.rmtree(export_dir)
        print("   🧹 Dossier temporaire nettoyé")

        return True

    except Exception as e:
        print(f"   ❌ Erreur lors de l'upload: {e}")
        return False

    finally:
        print()
        print("=" * 80)
        print("✅ ENREGISTREMENT TERMINÉ")
        print("=" * 80)
        print()
        print(f"🔗 Modèle disponible sur: https://huggingface.co/{hf_repo_id}")
        print("📝 Pour utiliser dans app.py:")
        print(f'   model = mlflow.sklearn.load_model("hf://{hf_repo_id}")')


if __name__ == "__main__":
    # Utiliser le meilleur run (le plus récent)
    RUN_ID = "2dd66b2b125646e19cf123c6944c9185"

    success = register_model_to_hf(
        run_id=RUN_ID, hf_repo_id="ASI-Engineer/employee-turnover-model"
    )

    if not success:
        print("\n⚠️  Enregistrement incomplet. Vérifiez HF_TOKEN.")
        exit(1)
