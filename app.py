#!/usr/bin/env python3
"""
Interface Gradio pour tester le modèle Employee Turnover en production.

Déploiement sur Hugging Face Spaces pour tests rapides.
Version de démonstration - Interface complète en développement.
"""
import gradio as gr
import mlflow
import mlflow.sklearn


# Configuration MLflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")

# Charger le modèle le plus récent
MODEL_URI = "models:/Employee_Turnover_Model/latest"
# Fallback: utiliser un run_id spécifique si le modèle n'est pas enregistré
FALLBACK_RUN_ID = "2dd66b2b125646e19cf123c6944c9185"


def load_model():
    """Charge le modèle depuis MLflow."""
    try:
        model = mlflow.sklearn.load_model(MODEL_URI)
        print(f"✅ Modèle chargé depuis Model Registry: {MODEL_URI}")
        return model
    except Exception as e:
        print(f"⚠️ Model Registry non disponible, utilisation du run_id: {e}")
        try:
            model = mlflow.sklearn.load_model(f"runs:/{FALLBACK_RUN_ID}/model")
            print(f"✅ Modèle chargé depuis run_id: {FALLBACK_RUN_ID}")
            return model
        except Exception as e2:
            print(f"❌ Erreur lors du chargement du modèle: {e2}")
            return None


# Charger le modèle au démarrage
try:
    model = load_model()
    MODEL_LOADED = model is not None
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle: {e}")
    MODEL_LOADED = False
    model = None


def get_model_info():
    """Retourne les informations sur le modèle."""
    if not MODEL_LOADED:
        return {
            "status": "❌ Modèle non disponible",
            "error": "Le modèle n'a pas pu être chargé depuis MLflow",
            "solution": "Vérifiez que main.py a bien été exécuté pour entraîner le modèle",
        }

    try:
        # Obtenir des informations sur le modèle
        client = mlflow.MlflowClient()
        runs = client.search_runs(
            experiment_ids=["1"], order_by=["start_time DESC"], max_results=1
        )

        if runs:
            run = runs[0]
            metrics = run.data.metrics
            return {
                "status": "✅ Modèle chargé avec succès",
                "run_id": run.info.run_id[:8],
                "f1_score": f"{metrics.get('f1_score', 0):.4f}",
                "accuracy": f"{metrics.get('accuracy', 0):.4f}",
                "features": "~50 features (après preprocessing)",
                "algorithme": "XGBoost + SMOTE",
                "info": "Interface de prédiction en développement - API FastAPI à venir",
            }
        else:
            return {
                "status": "✅ Modèle chargé",
                "info": "Pas de métriques disponibles",
                "run_id": FALLBACK_RUN_ID[:8],
            }

    except Exception as e:
        return {"status": "✅ Modèle chargé (info limitées)", "error": str(e)}


# Interface Gradio
with gr.Blocks(
    title="Employee Turnover Prediction - DEV", theme=gr.themes.Soft()
) as demo:
    gr.Markdown("# 🎯 Prédiction du Turnover - Employee Attrition")
    gr.Markdown("## Environment DEV - Test de déploiement CI/CD")

    gr.Markdown(
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

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🔍 Informations sur le modèle")
            check_btn = gr.Button("📊 Vérifier le statut du modèle", variant="primary")

        with gr.Column():
            model_output = gr.JSON(label="Statut")

    check_btn.click(fn=get_model_info, inputs=[], outputs=model_output)

    gr.Markdown("---")

    gr.Markdown(
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
