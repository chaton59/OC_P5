#!/usr/bin/env python3
"""
Interface Gradio pour tester le modèle Employee Turnover en production.

Déploiement sur Hugging Face Spaces pour tests rapides.
"""
import gradio as gr
import mlflow
import mlflow.sklearn
import pandas as pd


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
        model = mlflow.sklearn.load_model(f"runs:/{FALLBACK_RUN_ID}/model")
        print(f"✅ Modèle chargé depuis run_id: {FALLBACK_RUN_ID}")
        return model


# Charger le modèle au démarrage
try:
    model = load_model()
    MODEL_LOADED = True
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle: {e}")
    MODEL_LOADED = False
    model = None


def predict_turnover(
    satisfaction_level: float,
    last_evaluation: float,
    number_project: int,
    average_monthly_hours: int,
    time_spend_company: int,
    work_accident: int,
    promotion_last_5years: int,
    department: str,
    salary: str,
):
    """
    Prédiction du turnover d'un employé.
    
    Returns:
        dict: Probabilités de départ (0: reste, 1: part)
    """
    if not MODEL_LOADED or model is None:
        return {
            "error": "Modèle non disponible. Vérifiez la configuration MLflow."
        }
    
    try:
        # Créer le DataFrame d'input (ajuster les colonnes selon votre preprocessing)
        input_data = pd.DataFrame({
            "satisfaction_level": [satisfaction_level],
            "last_evaluation": [last_evaluation],
            "number_project": [number_project],
            "average_montly_hours": [average_monthly_hours],
            "time_spend_company": [time_spend_company],
            "Work_accident": [work_accident],
            "promotion_last_5years": [promotion_last_5years],
            "sales": [department],  # Nom colonne selon votre dataset
            "salary": [salary],
        })
        
        # Prédiction
        proba = model.predict_proba(input_data)[0]
        prediction = model.predict(input_data)[0]
        
        result = {
            "Probabilité de rester (0)": f"{proba[0]:.2%}",
            "Probabilité de partir (1)": f"{proba[1]:.2%}",
            "Prédiction": "⚠️ Risque de départ" if prediction == 1 else "✅ Employé stable",
            "Recommandation": (
                "Action requise: Entretien RH recommandé" 
                if proba[1] > 0.7 
                else "Suivi normal"
            )
        }
        
        return result
        
    except Exception as e:
        return {"error": f"Erreur lors de la prédiction: {str(e)}"}


# Interface Gradio
with gr.Blocks(title="Employee Turnover Prediction", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎯 Prédiction du Turnover - Employee Attrition")
    gr.Markdown(
        "Prédisez le risque de départ d'un employé basé sur ses caractéristiques."
    )
    
    if not MODEL_LOADED:
        gr.Markdown("## ⚠️ ATTENTION: Modèle non chargé. Vérifiez la configuration MLflow.")
    
    with gr.Row():
        with gr.Column():
            satisfaction = gr.Slider(
                0, 1, value=0.7, step=0.01,
                label="Niveau de satisfaction (0-1)"
            )
            evaluation = gr.Slider(
                0, 1, value=0.8, step=0.01,
                label="Dernière évaluation (0-1)"
            )
            projects = gr.Slider(
                2, 7, value=3, step=1,
                label="Nombre de projets"
            )
            hours = gr.Slider(
                96, 310, value=200, step=1,
                label="Heures mensuelles moyennes"
            )
            
        with gr.Column():
            tenure = gr.Slider(
                2, 10, value=3, step=1,
                label="Années dans l'entreprise"
            )
            accident = gr.Radio(
                [0, 1], value=0,
                label="Accident de travail (0: Non, 1: Oui)"
            )
            promotion = gr.Radio(
                [0, 1], value=0,
                label="Promotion 5 dernières années (0: Non, 1: Oui)"
            )
            department = gr.Dropdown(
                ["sales", "technical", "support", "IT", "product_mng", 
                 "marketing", "RandD", "accounting", "hr", "management"],
                value="sales",
                label="Département"
            )
            salary_level = gr.Radio(
                ["low", "medium", "high"], value="medium",
                label="Niveau de salaire"
            )
    
    predict_btn = gr.Button("🔮 Prédire le risque de départ", variant="primary")
    
    output = gr.JSON(label="Résultat de la prédiction")
    
    predict_btn.click(
        fn=predict_turnover,
        inputs=[
            satisfaction, evaluation, projects, hours, tenure,
            accident, promotion, department, salary_level
        ],
        outputs=output
    )
    
    gr.Markdown("---")
    gr.Markdown(
        """
        ### 📊 À propos
        - **Modèle**: XGBoost avec SMOTE (équilibrage des classes)
        - **Métriques**: Optimisé pour F1-Score
        - **MLflow**: Tracking et versioning des modèles
        - **Déploiement**: CI/CD automatisé via GitHub Actions
        """
    )
    
    # Exemples prédéfinis
    gr.Examples(
        examples=[
            [0.38, 0.53, 2, 157, 3, 0, 0, "sales", "low"],  # Risque élevé
            [0.80, 0.86, 5, 262, 6, 0, 1, "management", "high"],  # Risque faible
            [0.11, 0.88, 7, 272, 4, 0, 0, "technical", "medium"],  # Risque élevé
        ],
        inputs=[
            satisfaction, evaluation, projects, hours, tenure,
            accident, promotion, department, salary_level
        ],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
