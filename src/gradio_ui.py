#!/usr/bin/env python3
"""
Interface Gradio pour l'API Employee Turnover Prediction.

Cette interface permet de:
- Tester les prédictions de manière interactive
- Visualiser la documentation de l'API
- Comprendre les champs requis
"""
import os
from typing import cast

import gradio as gr

from src.models import get_model_info, load_model
from src.preprocessing import preprocess_for_prediction
from src.schemas import (
    AyantEnfantsEnum,
    DepartementEnum,
    DomaineEtudeEnum,
    EmployeeInput,
    FrequenceDeplacementEnum,
    GenreEnum,
    HeureSupplementairesEnum,
    PosteEnum,
    StatutMaritalEnum,
)


def predict_turnover(
    # SONDAGE
    nombre_participation_pee: int,
    nb_formations_suivies: int,
    nombre_employee_sous_responsabilite: int,
    distance_domicile_travail: int,
    niveau_education: int,
    domaine_etude: str,
    ayant_enfants: str,
    frequence_deplacement: str,
    annees_depuis_la_derniere_promotion: int,
    annes_sous_responsable_actuel: int,
    # EVALUATION
    satisfaction_employee_environnement: int,
    note_evaluation_precedente: int,
    niveau_hierarchique_poste: int,
    satisfaction_employee_nature_travail: int,
    satisfaction_employee_equipe: int,
    satisfaction_employee_equilibre_pro_perso: int,
    note_evaluation_actuelle: int,
    heure_supplementaires: str,
    augementation_salaire_precedente: float,
    # SIRH
    age: int,
    genre: str,
    revenu_mensuel: float,
    statut_marital: str,
    departement: str,
    poste: str,
    nombre_experiences_precedentes: int,
    nombre_heures_travailless: int,
    annee_experience_totale: int,
    annees_dans_l_entreprise: int,
    annees_dans_le_poste_actuel: int,
) -> str:
    """Effectue une prédiction de turnover directement via le modèle."""
    try:
        # Créer l'objet EmployeeInput avec validation Pydantic
        employee = EmployeeInput(
            nombre_participation_pee=int(nombre_participation_pee),
            nb_formations_suivies=int(nb_formations_suivies),
            nombre_employee_sous_responsabilite=int(
                nombre_employee_sous_responsabilite
            ),
            distance_domicile_travail=int(distance_domicile_travail),
            niveau_education=int(niveau_education),
            domaine_etude=cast(DomaineEtudeEnum, domaine_etude),
            ayant_enfants=cast(AyantEnfantsEnum, ayant_enfants),
            frequence_deplacement=cast(FrequenceDeplacementEnum, frequence_deplacement),
            annees_depuis_la_derniere_promotion=int(
                annees_depuis_la_derniere_promotion
            ),
            annes_sous_responsable_actuel=int(annes_sous_responsable_actuel),
            satisfaction_employee_environnement=int(
                satisfaction_employee_environnement
            ),
            note_evaluation_precedente=int(note_evaluation_precedente),
            niveau_hierarchique_poste=int(niveau_hierarchique_poste),
            satisfaction_employee_nature_travail=int(
                satisfaction_employee_nature_travail
            ),
            satisfaction_employee_equipe=int(satisfaction_employee_equipe),
            satisfaction_employee_equilibre_pro_perso=int(
                satisfaction_employee_equilibre_pro_perso
            ),
            note_evaluation_actuelle=int(note_evaluation_actuelle),
            heure_supplementaires=cast(HeureSupplementairesEnum, heure_supplementaires),
            augementation_salaire_precedente=float(augementation_salaire_precedente),
            age=int(age),
            genre=cast(GenreEnum, genre),
            revenu_mensuel=float(revenu_mensuel),
            statut_marital=cast(StatutMaritalEnum, statut_marital),
            departement=cast(DepartementEnum, departement),
            poste=cast(PosteEnum, poste),
            nombre_experiences_precedentes=int(nombre_experiences_precedentes),
            nombre_heures_travailless=int(nombre_heures_travailless),
            annee_experience_totale=int(annee_experience_totale),
            annees_dans_l_entreprise=int(annees_dans_l_entreprise),
            annees_dans_le_poste_actuel=int(annees_dans_le_poste_actuel),
        )

        # Preprocessing
        features = preprocess_for_prediction(employee)

        # Charger le modèle et prédire
        model = load_model()
        prediction = int(model.predict(features)[0])
        proba = model.predict_proba(features)[0]
        prob_0 = float(proba[0])
        prob_1 = float(proba[1])

        # Déterminer le niveau de risque
        if prob_1 < 0.3:
            risk_level = "Low"
        elif prob_1 < 0.7:
            risk_level = "Medium"
        else:
            risk_level = "High"

        # Affichage
        if risk_level == "High":
            risk_emoji = "🔴 RISQUE ÉLEVÉ"
        elif risk_level == "Medium":
            risk_emoji = "🟠 RISQUE MOYEN"
        else:
            risk_emoji = "🟢 RISQUE FAIBLE"

        confidence = max(prob_0, prob_1) * 100

        # Enregistrer dans la base de données (uniquement en local)
        db_status = "ℹ️ DB désactivée sur HF Spaces"
        try:
            # Vérifier si on est sur HF Spaces (variable d'environnement)
            if os.getenv("SPACE_ID") is None:  # Pas sur HF Spaces
                from sqlalchemy import create_engine
                from sqlalchemy.orm import sessionmaker

                from src.config import get_settings

                settings = get_settings()
                engine = create_engine(settings.DATABASE_URL)
                Session = sessionmaker(bind=engine)
                session = Session()

                # Importer le modèle MLLog
                from db_models import MLLog

                # Créer le log
                log_entry = MLLog(
                    input_json=employee.dict(),  # Convertir Pydantic en dict
                    prediction="Oui" if prediction == 1 else "Non",
                )
                session.add(log_entry)
                session.commit()
                session.close()

                db_status = "✅ Enregistré en DB"
        except Exception as db_error:
            db_status = f"⚠️ Erreur DB: {str(db_error)}"

        result = f"""
## {risk_emoji}

### Résultat de la prédiction
- **Prédiction**: {"Départ probable" if prediction == 1 else "Maintien probable"}
- **Confiance**: {confidence:.1f}%
- **Probabilité de départ**: {prob_1 * 100:.1f}%
- **Probabilité de maintien**: {prob_0 * 100:.1f}%

### Base de données
{db_status}

### Interprétation
{"⚠️ Cet employé présente des facteurs de risque de départ. Il est recommandé d'engager un dialogue pour comprendre ses attentes." if prediction == 1 else "✅ Cet employé semble stable. Continuez à maintenir un environnement de travail positif."}
"""
        return result

    except Exception as e:
        return f"❌ **Erreur**: {str(e)}"


# Documentation de l'API
API_DOCS = """
# 🚀 Employee Turnover Prediction API

## Description
Cette API prédit le risque de départ (turnover) d'un employé en utilisant un modèle
de Machine Learning entraîné sur des données RH.

## Endpoints disponibles

### `GET /`
Page d'accueil avec informations sur l'API.

### `GET /health`
Vérification de l'état de l'API.
```bash
curl https://asi-engineer-oc-p5-dev.hf.space/health
```

### `GET /docs`
Documentation Swagger interactive.

### `POST /predict`
Effectue une prédiction de turnover.

## Exemple d'utilisation avec curl

```bash
curl -X POST https://asi-engineer-oc-p5-dev.hf.space/predict \\
  -H "Content-Type: application/json" \\
  -d '{
    "nombre_participation_pee": 0,
    "nb_formations_suivies": 2,
    "nombre_employee_sous_responsabilite": 1,
    "distance_domicile_travail": 15,
    "niveau_education": 3,
    "domaine_etude": "Infra & Cloud",
    "ayant_enfants": "Y",
    "frequence_deplacement": "Occasionnel",
    "annees_depuis_la_derniere_promotion": 2,
    "annes_sous_responsable_actuel": 5,
    "satisfaction_employee_environnement": 3,
    "note_evaluation_precedente": 4,
    "niveau_hierarchique_poste": 2,
    "satisfaction_employee_nature_travail": 3,
    "satisfaction_employee_equipe": 3,
    "satisfaction_employee_equilibre_pro_perso": 2,
    "note_evaluation_actuelle": 4,
    "heure_supplementaires": "Non",
    "augementation_salaire_precedente": 5.5,
    "age": 35,
    "genre": "M",
    "revenu_mensuel": 4500.0,
    "statut_marital": "Marié(e)",
    "departement": "Commercial",
    "poste": "Manager",
    "nombre_experiences_precedentes": 3,
    "nombre_heures_travailless": 80,
    "annee_experience_totale": 10,
    "annees_dans_l_entreprise": 5,
    "annees_dans_le_poste_actuel": 2
  }'
```

## Exemple avec Python

```python
import requests

url = "https://asi-engineer-oc-p5-dev.hf.space/predict"

data = {
    "nombre_participation_pee": 0,
    "nb_formations_suivies": 2,
    "nombre_employee_sous_responsabilite": 1,
    "distance_domicile_travail": 15,
    "niveau_education": 3,
    "domaine_etude": "Infra & Cloud",
    "ayant_enfants": "Y",
    "frequence_deplacement": "Occasionnel",
    "annees_depuis_la_derniere_promotion": 2,
    "annes_sous_responsable_actuel": 5,
    "satisfaction_employee_environnement": 3,
    "note_evaluation_precedente": 4,
    "niveau_hierarchique_poste": 2,
    "satisfaction_employee_nature_travail": 3,
    "satisfaction_employee_equipe": 3,
    "satisfaction_employee_equilibre_pro_perso": 2,
    "note_evaluation_actuelle": 4,
    "heure_supplementaires": "Non",
    "augementation_salaire_precedente": 5.5,
    "age": 35,
    "genre": "M",
    "revenu_mensuel": 4500.0,
    "statut_marital": "Marié(e)",
    "departement": "Commercial",
    "poste": "Manager",
    "nombre_experiences_precedentes": 3,
    "nombre_heures_travailless": 80,
    "annee_experience_totale": 10,
    "annees_dans_l_entreprise": 5,
    "annees_dans_le_poste_actuel": 2
}

response = requests.post(url, json=data)
print(response.json())
```

## Réponse attendue

```json
{
  "prediction": 0,
  "probability": {
    "stay": 0.85,
    "leave": 0.15
  },
  "risk_level": "low",
  "model_version": "1.0.0"
}
```

## Codes d'erreur

| Code | Description |
|------|-------------|
| 200 | Succès |
| 422 | Données invalides (validation Pydantic) |
| 429 | Trop de requêtes (rate limit: 20/min) |
| 500 | Erreur serveur |

## Modèle utilisé

- **Type**: XGBoost Pipeline
- **Source**: HuggingFace Hub (`ASI-Engineer/employee-turnover-model`)
- **Features**: 25 variables RH (sondage, évaluation, SIRH)
"""


def create_gradio_interface():
    """Crée l'interface Gradio complète."""

    # Obtenir les infos du modèle
    try:
        model_info = get_model_info()
        model_status = f"✅ Modèle chargé: {model_info.get('model_type', 'Unknown')}"
    except Exception:
        model_status = "⏳ Modèle en cours de chargement..."

    with gr.Blocks(
        title="Employee Turnover Prediction",
    ) as demo:
        gr.Markdown(
            """
        # 🏢 Employee Turnover Prediction

        Prédisez le risque de départ d'un employé grâce au Machine Learning.

        **Naviguez entre les onglets** pour utiliser l'interface de prédiction
        ou consulter la documentation de l'API.
        """
        )

        gr.Markdown(f"**Statut**: {model_status}")

        with gr.Tabs():
            # Onglet Prédiction
            with gr.TabItem("🎯 Prédiction"):
                gr.Markdown("### Remplissez les informations de l'employé")

                with gr.Row():
                    # Colonne SONDAGE
                    with gr.Column():
                        gr.Markdown("#### 📋 Données Sondage")
                        nombre_participation_pee = gr.Slider(
                            0, 3, value=0, step=1, label="Participations PEE"
                        )
                        nb_formations_suivies = gr.Slider(
                            0, 6, value=2, step=1, label="Formations suivies"
                        )
                        nombre_employee_sous_responsabilite = gr.Number(
                            value=1,
                            label="Employés sous responsabilité",
                            interactive=False,
                        )
                        distance_domicile_travail = gr.Slider(
                            1, 30, value=10, step=1, label="Distance domicile (km)"
                        )
                        niveau_education = gr.Slider(
                            1, 5, value=3, step=1, label="Niveau éducation (1-5)"
                        )
                        domaine_etude = gr.Dropdown(
                            [
                                "Infra & Cloud",
                                "Transformation Digitale",
                                "Marketing",
                                "Entrepreunariat",
                                "Ressources Humaines",
                                "Autre",
                            ],
                            value="Infra & Cloud",
                            label="Domaine d'études",
                        )
                        ayant_enfants = gr.Radio(
                            ["Y", "N"], value="N", label="A des enfants"
                        )
                        frequence_deplacement = gr.Dropdown(
                            ["Aucun", "Occasionnel", "Frequent"],
                            value="Occasionnel",
                            label="Fréquence déplacements",
                        )
                        annees_depuis_la_derniere_promotion = gr.Slider(
                            0, 15, value=2, step=1, label="Années depuis promotion"
                        )
                        annes_sous_responsable_actuel = gr.Slider(
                            0, 17, value=3, step=1, label="Années sous responsable"
                        )

                    # Colonne EVALUATION
                    with gr.Column():
                        gr.Markdown("#### 📊 Données Évaluation")
                        satisfaction_employee_environnement = gr.Slider(
                            1, 4, value=3, step=1, label="Satisfaction environnement"
                        )
                        note_evaluation_precedente = gr.Slider(
                            1, 4, value=3, step=1, label="Évaluation précédente"
                        )
                        niveau_hierarchique_poste = gr.Slider(
                            1, 5, value=2, step=1, label="Niveau hiérarchique"
                        )
                        satisfaction_employee_nature_travail = gr.Slider(
                            1, 4, value=3, step=1, label="Satisfaction nature travail"
                        )
                        satisfaction_employee_equipe = gr.Slider(
                            1, 4, value=3, step=1, label="Satisfaction équipe"
                        )
                        satisfaction_employee_equilibre_pro_perso = gr.Slider(
                            1, 4, value=3, step=1, label="Équilibre pro/perso"
                        )
                        note_evaluation_actuelle = gr.Slider(
                            3, 4, value=3, step=1, label="Évaluation actuelle"
                        )
                        heure_supplementaires = gr.Radio(
                            ["Oui", "Non"], value="Non", label="Heures supplémentaires"
                        )
                        augementation_salaire_precedente = gr.Slider(
                            0,
                            25,
                            value=5.0,
                            step=0.5,
                            label="Augmentation précédente (%)",
                        )

                    # Colonne SIRH
                    with gr.Column():
                        gr.Markdown("#### 👤 Données SIRH")
                        age = gr.Slider(18, 60, value=35, step=1, label="Âge")
                        genre = gr.Radio(["M", "F"], value="M", label="Genre")
                        revenu_mensuel = gr.Slider(
                            1000,
                            20000,
                            value=4500,
                            step=100,
                            label="Revenu mensuel (€)",
                        )
                        statut_marital = gr.Dropdown(
                            ["Célibataire", "Marié(e)", "Divorcé(e)"],
                            value="Célibataire",
                            label="Statut marital",
                        )
                        departement = gr.Dropdown(
                            ["Commercial", "Consulting", "Ressources Humaines"],
                            value="Commercial",
                            label="Département",
                        )
                        poste = gr.Dropdown(
                            [
                                "Cadre Commercial",
                                "Assistant de Direction",
                                "Consultant",
                                "Tech Lead",
                                "Manager",
                                "Senior Manager",
                                "Représentant Commercial",
                                "Directeur Technique",
                                "Ressources Humaines",
                            ],
                            value="Consultant",
                            label="Poste",
                        )
                        nombre_experiences_precedentes = gr.Slider(
                            0, 9, value=2, step=1, label="Expériences précédentes"
                        )
                        nombre_heures_travailless = gr.Number(
                            value=80, label="Heures travaillées/sem", interactive=False
                        )
                        annee_experience_totale = gr.Slider(
                            0, 40, value=10, step=1, label="Années d'expérience totale"
                        )
                        annees_dans_l_entreprise = gr.Slider(
                            0, 40, value=5, step=1, label="Années dans l'entreprise"
                        )
                        annees_dans_le_poste_actuel = gr.Slider(
                            0, 18, value=2, step=1, label="Années dans le poste"
                        )

                # Bouton et résultat
                predict_btn = gr.Button(
                    "🔮 Prédire le risque de départ", variant="primary"
                )
                result = gr.Markdown(label="Résultat")

                predict_btn.click(
                    fn=predict_turnover,
                    inputs=[
                        nombre_participation_pee,
                        nb_formations_suivies,
                        nombre_employee_sous_responsabilite,
                        distance_domicile_travail,
                        niveau_education,
                        domaine_etude,
                        ayant_enfants,
                        frequence_deplacement,
                        annees_depuis_la_derniere_promotion,
                        annes_sous_responsable_actuel,
                        satisfaction_employee_environnement,
                        note_evaluation_precedente,
                        niveau_hierarchique_poste,
                        satisfaction_employee_nature_travail,
                        satisfaction_employee_equipe,
                        satisfaction_employee_equilibre_pro_perso,
                        note_evaluation_actuelle,
                        heure_supplementaires,
                        augementation_salaire_precedente,
                        age,
                        genre,
                        revenu_mensuel,
                        statut_marital,
                        departement,
                        poste,
                        nombre_experiences_precedentes,
                        nombre_heures_travailless,
                        annee_experience_totale,
                        annees_dans_l_entreprise,
                        annees_dans_le_poste_actuel,
                    ],
                    outputs=result,
                    api_name="predict",
                )

            # Onglet Documentation
            with gr.TabItem("📚 Documentation API"):
                gr.Markdown(API_DOCS)

            # Onglet À propos
            with gr.TabItem("ℹ️ À propos"):
                gr.Markdown(
                    """
                ## À propos de ce projet

                ### 🎓 Contexte
                Ce projet a été réalisé dans le cadre du **Projet 5 OpenClassrooms** :
                "Déployez votre modèle de Machine Learning".

                ### 🎯 Objectif
                Développer une API de prédiction du turnover (départ) des employés,
                permettant aux équipes RH d'anticiper et de prévenir les départs.

                ### 🛠️ Technologies utilisées
                - **FastAPI** : Framework API REST performant
                - **XGBoost** : Modèle de Machine Learning
                - **Gradio** : Interface utilisateur
                - **HuggingFace Hub** : Hébergement du modèle
                - **HuggingFace Spaces** : Déploiement de l'application
                - **GitHub Actions** : CI/CD automatisé

                ### 📊 Le modèle
                Le modèle a été entraîné sur des données RH comprenant :
                - Données de sondage de satisfaction
                - Données d'évaluation de performance
                - Données administratives SIRH

                ### 🔗 Liens utiles
                - [GitHub Repository](https://github.com/chaton59/OC_P5)
                - [API Documentation (Swagger)](/docs)
                - [HuggingFace Model](https://huggingface.co/ASI-Engineer/employee-turnover-model)

                ### 👤 Auteur
                Projet OpenClassrooms - Formation Data Scientist
                """
                )

    return demo


def launch_standalone():
    """Lance Gradio en mode standalone (pour HuggingFace Spaces)."""
    import sys
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True
    )
    logger = logging.getLogger(__name__)

    logger.info("🚀 Démarrage de l'application Gradio...")
    logger.info(f"Python version: {sys.version}")

    # Pré-charger le modèle pour éviter le timeout au premier appel
    logger.info("📦 Pré-chargement du modèle...")
    try:
        from src.models import load_model

        model = load_model()
        logger.info(f"✅ Modèle chargé: {type(model).__name__}")
    except Exception as e:
        logger.warning(f"⚠️ Erreur chargement modèle au démarrage: {e}")
        logger.warning("L'application continuera sans préchargement du modèle")

    try:
        logger.info("🎨 Création de l'interface Gradio...")
        demo = create_gradio_interface()
        logger.info("✅ Interface Gradio créée avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de l'interface: {e}", exc_info=True)
        sys.exit(1)

    # Configuration pour HuggingFace Spaces
    logger.info("🌐 Lancement du serveur sur 0.0.0.0:7860...")
    sys.stdout.flush()
    sys.stderr.flush()

    try:
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            quiet=False,
        )
    except Exception as e:
        logger.error(f"❌ Erreur lors du lancement du serveur: {e}", exc_info=True)
        sys.exit(1)


# Pour lancer en standalone
if __name__ == "__main__":
    launch_standalone()
