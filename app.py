#!/usr/bin/env python3
"""
Interface Gradio pour tester le modèle Employee Turnover en production.

Déploiement sur Hugging Face Spaces pour tests rapides.
Version de démonstration - Interface complète en développement.
"""
from pathlib import Path

import gradio as gr
import mlflow
import mlflow.pyfunc
from huggingface_hub import hf_hub_download

# Configuration
HF_MODEL_REPO = "ASI-Engineer/employee-turnover-model"
FALLBACK_RUN_ID = "40e43c8e425345bab3d19f27eb8fe5d8"


def load_model():
    """
    Charge le modèle depuis Hugging Face Hub (prod) ou MLflow local (dev).

    Ordre de priorité:
    1. HF Hub (modèle déployé en production)
    2. MLflow local (développement local)
    """
    # Essayer HF Hub en premier (production)
    try:
        # Download model from HF Hub
        model_path = hf_hub_download(
            repo_id=HF_MODEL_REPO, filename="model/model.pkl", repo_type="model"
        )
        model = mlflow.pyfunc.load_model(str(Path(model_path).parent))  # type: ignore[attr-defined]
        print(f"✅ Modèle chargé depuis HF Hub: {HF_MODEL_REPO}")
        return model, "HF Hub"
    except Exception as e:
        print(f"⚠️ HF Hub non disponible: {e}")

    # Fallback: MLflow local (développement)
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    try:
        # Essayer Model Registry d'abord
        model = mlflow.pyfunc.load_model("models:/XGBoost_Employee_Turnover/latest")  # type: ignore[attr-defined]
        print("✅ Modèle chargé depuis MLflow Model Registry")
        return model, "MLflow Registry"
    except Exception:
        try:
            # Fallback sur run ID
            model = mlflow.pyfunc.load_model(f"runs:/{FALLBACK_RUN_ID}/model")  # type: ignore[attr-defined]
            print(f"✅ Modèle chargé depuis MLflow run: {FALLBACK_RUN_ID}")
            return model, "MLflow Local"
        except Exception as e2:
            print(f"❌ Erreur chargement MLflow: {e2}")
            return None, "Error"


# Charger le modèle au démarrage
try:
    model, model_source = load_model()
    MODEL_LOADED = model is not None
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle: {e}")
    MODEL_LOADED = False
    model = None
    model_source = "Error"


def get_model_info():
    """Retourne les informations sur le modèle."""
    if not MODEL_LOADED:
        return {
            "status": "❌ Modèle non disponible",
            "error": "Le modèle n'a pas pu être chargé",
            "solution": "Vérifiez que le modèle est bien enregistré sur HF Hub ou entraîné localement",
        }

    try:
        info = {
            "status": "✅ Modèle chargé avec succès",
            "source": model_source,
            "model_type": type(model).__name__,
            "features": "~50 features (après preprocessing)",
            "algorithme": "XGBoost + SMOTE",
            "hf_hub_repo": HF_MODEL_REPO if model_source == "HF Hub" else "N/A",
        }

        # Si MLflow local, ajouter les métriques
        if model_source == "MLflow Local":
            mlflow.set_tracking_uri("sqlite:///mlflow.db")
            client = mlflow.MlflowClient()
            runs = client.search_runs(
                experiment_ids=["1"], order_by=["start_time DESC"], max_results=1
            )
            if runs:
                run = runs[0]
                metrics = run.data.metrics
                info.update(
                    {
                        "run_id": run.info.run_id[:8],
                        "f1_score": f"{metrics.get('f1_score', 0):.4f}",
                        "accuracy": f"{metrics.get('accuracy', 0):.4f}",
                    }
                )

        info["info"] = "Interface de prédiction en développement - API FastAPI à venir"
        return info

    except Exception as e:
        return {"status": "✅ Modèle chargé (info limitées)", "error": str(e)}


# Interface Gradio
with gr.Blocks(  # type: ignore[attr-defined]
    title="Employee Turnover Prediction - DEV", theme=gr.themes.Soft()  # type: ignore[attr-defined]
) as demo:
    gr.Markdown("# 🎯 Prédiction du Turnover - Employee Attrition")  # type: ignore[attr-defined]
    gr.Markdown("## Environment DEV - Test de déploiement CI/CD")  # type: ignore[attr-defined]

    gr.Markdown(  # type: ignore[attr-defined]
        """
    ### 📊 Statut du projet

    Ce Space est synchronisé automatiquement depuis GitHub (branche `dev`).

    **Actuellement disponible :**
    - ✅ Pipeline d'entraînement MLflow complet (`main.py`)
    - ✅ Déploiement automatique CI/CD (GitHub Actions → HF Spaces)
    - ✅ Tests unitaires et linting automatisés

    **En développement :**
    - 🚧 Interface de prédiction interactive
    - 🚧 API FastAPI avec endpoints de prédiction
    - 🚧 Intégration PostgreSQL pour tracking des prédictions
    """
    )

    with gr.Row():  # type: ignore[attr-defined]
        with gr.Column():  # type: ignore[attr-defined]
            gr.Markdown("### 🔍 Informations sur le modèle")  # type: ignore[attr-defined]
            check_btn = gr.Button("📊 Vérifier le statut du modèle", variant="primary")  # type: ignore[attr-defined]

        with gr.Column():  # type: ignore[attr-defined]
            model_output = gr.JSON(label="Statut")  # type: ignore[attr-defined]

    check_btn.click(fn=get_model_info, inputs=[], outputs=model_output)

    gr.Markdown("---")  # type: ignore[attr-defined]

    gr.Markdown(  # type: ignore[attr-defined]
        """
    ### 🛠️ Prochaines étapes (selon etapes.txt)

    1. **Étape 3** : Développement API FastAPI
       - Endpoints de prédiction avec validation Pydantic
       - Chargement dynamique des preprocessing artifacts (scaler, encoders)
       - Documentation Swagger/OpenAPI automatique

    2. **Étape 4** : Intégration PostgreSQL
       - Stockage des inputs/outputs des prédictions
       - Traçabilité complète des requêtes

    3. **Étape 5** : Tests unitaires et fonctionnels
       - Tests des endpoints API
       - Tests de charge et performance
       - Couverture de code avec pytest-cov

    ### 📚 Documentation
    - **Repository GitHub** : [chaton59/OC_P5](https://github.com/chaton59/OC_P5)
    - **MLflow Tracking** : Disponible en local (`./scripts/start_mlflow.sh`)
    - **Métriques** : F1-Score optimisé, gestion classes déséquilibrées (SMOTE)
    """
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
