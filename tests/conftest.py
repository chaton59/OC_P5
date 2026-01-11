#!/usr/bin/env python3
"""
Configuration pytest et fixtures pour les tests de l'API.

Ce module fournit des fixtures réutilisables pour tous les tests,
notamment un client de test FastAPI et des données d'exemple.
"""
import os

import pytest
from fastapi.testclient import TestClient

# Forcer le mode DEBUG pour les tests (désactive auth)
# flake8: noqa: E402  # Import de l'app doit se faire après configuration DEBUG
os.environ["DEBUG"] = "True"
os.environ["API_KEY"] = "test-api-key-12345"
os.environ["HF_TOKEN"] = "test-hf-token"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

from api import app


@pytest.fixture(autouse=True)
def mock_model_loading(monkeypatch):
    """
    Mock automatique du chargement du modèle pour éviter les appels à HF Hub pendant les tests.

    Crée un modèle XGBoost factice qui retourne toujours une prédiction de 0.5.
    """

    # Créer un mock du modèle XGBoost
    class MockXGBoostModel:
        def __init__(self):
            self.__class__.__name__ = "Pipeline"  # Pour faire passer les tests

        def predict_proba(self, X):
            """Retourne toujours [0.5, 0.5] pour les probabilités."""
            import numpy as np

            n_samples = X.shape[0] if hasattr(X, "shape") else len(X)
            return np.array([[0.5, 0.5]] * n_samples)

        def predict(self, X):
            """Retourne toujours 0 (pas de turnover)."""
            import numpy as np

            n_samples = X.shape[0] if hasattr(X, "shape") else len(X)
            return np.array([0] * n_samples)

    # Mock de la fonction load_model
    mock_model = MockXGBoostModel()
    monkeypatch.setattr("src.models.load_model", lambda: mock_model)
    monkeypatch.setattr("src.models._model_cache", mock_model)  # Aussi patcher le cache

    # Par sécurité, mocker aussi hf_hub_download pour éviter tout accès réseau accidentel
    try:
        import tempfile
        from huggingface_hub import hf_hub_download

        dummy_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pkl")
        dummy_path = dummy_file.name
        dummy_file.close()

        monkeypatch.setattr(
            "huggingface_hub.hf_hub_download", lambda *args, **kwargs: dummy_path
        )
    except Exception:
        # Si huggingface_hub n'est pas disponible, ignorer silencieusement
        pass


@pytest.fixture
def client():
    """
    Client de test FastAPI.

    Permet de faire des requêtes HTTP vers l'API sans lancer un serveur.

    Yields:
        TestClient: Client configuré pour tester l'API.

    Examples:
        >>> def test_health(client):
        ...     response = client.get("/health")
        ...     assert response.status_code == 200
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_employee_data():
    """
    Données valides d'un employé pour tester /predict.

    Returns:
        dict: Données complètes et valides selon le schéma Pydantic.
    """
    return {
        # SONDAGE
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
        # EVALUATION
        "satisfaction_employee_environnement": 3,
        "note_evaluation_precedente": 4,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_equilibre_pro_perso": 2,
        "note_evaluation_actuelle": 4,
        "heure_supplementaires": "Non",
        "augementation_salaire_precedente": 5.5,
        # SIRH
        "age": 35,
        "genre": "M",
        "revenu_mensuel": 4500.0,
        "statut_marital": "Marié(e)",
        "departement": "Commercial",
        "poste": "Manager",
        "nombre_experiences_precedentes": 3,
        "nombre_heures_travailless": 80,  # Fixe: 80
        "annee_experience_totale": 10,
        "annees_dans_l_entreprise": 5,
        "annees_dans_le_poste_actuel": 2,
    }


@pytest.fixture
def high_risk_employee_data():
    """
    Données d'un employé à haut risque de départ.

    Caractéristiques : faible satisfaction, pas de promotion, heures sup.

    Returns:
        dict: Données d'employé avec facteurs de risque élevés.
    """
    return {
        "nombre_participation_pee": 0,
        "nb_formations_suivies": 0,
        "nombre_employee_sous_responsabilite": 1,  # Fixe: 1
        "distance_domicile_travail": 29,  # Max: 29
        "niveau_education": 2,
        "domaine_etude": "Autre",
        "ayant_enfants": "N",
        "frequence_deplacement": "Frequent",
        "annees_depuis_la_derniere_promotion": 5,
        "annes_sous_responsable_actuel": 5,
        "satisfaction_employee_environnement": 1,
        "note_evaluation_precedente": 2,
        "niveau_hierarchique_poste": 1,
        "satisfaction_employee_nature_travail": 1,
        "satisfaction_employee_equipe": 1,
        "satisfaction_employee_equilibre_pro_perso": 1,
        "note_evaluation_actuelle": 3,  # Min: 3
        "heure_supplementaires": "Oui",
        "augementation_salaire_precedente": 0.0,
        "age": 28,
        "genre": "F",
        "revenu_mensuel": 2500.0,
        "statut_marital": "Célibataire",
        "departement": "Commercial",
        "poste": "Représentant Commercial",
        "nombre_experiences_precedentes": 1,
        "nombre_heures_travailless": 80,  # Fixe: 80
        "annee_experience_totale": 3,
        "annees_dans_l_entreprise": 3,
        "annees_dans_le_poste_actuel": 3,
    }


@pytest.fixture
def invalid_employee_data():
    """
    Données invalides pour tester la validation Pydantic.

    Returns:
        dict: Données avec erreurs de validation.
    """
    return {
        "nombre_participation_pee": -1,  # Négatif (invalide)
        "nb_formations_suivies": 999,  # Trop élevé (invalide)
        "age": 15,  # Trop jeune (invalide)
        "genre": "X",  # Genre invalide
        "departement": "InvalidDept",  # Département inexistant
        # ... manque plein de champs requis
    }


@pytest.fixture
def sample_dataset_rows():
    """
    Échantillon de données réelles du dataset pour tests variés.

    Charge quelques lignes des fichiers CSV et les fusionne pour fournir
    des données représentatives incluant des cas limites.

    Returns:
        list[dict]: Liste de dictionnaires avec données d'employés réelles.
    """
    import os

    import pandas as pd

    # Chemins des fichiers
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    sondage_file = os.path.join(data_dir, "extrait_sondage.csv")
    eval_file = os.path.join(data_dir, "extrait_eval.csv")
    sirh_file = os.path.join(data_dir, "extrait_sirh.csv")

    # Charger les dataframes
    df_sondage = pd.read_csv(sondage_file)
    df_eval = pd.read_csv(eval_file)
    df_sirh = pd.read_csv(sirh_file)

    # Fusionner horizontalement (même ordre)
    df_merged = pd.concat([df_sondage, df_eval, df_sirh], axis=1)
    df_merged = df_merged.loc[:, ~df_merged.columns.duplicated()]

    # Sélectionner quelques exemples représentatifs
    samples = []

    # Exemple 1: Employé qui a quitté (cas positif)
    quitter_row = df_merged[df_merged["a_quitte_l_entreprise"] == "Oui"].iloc[0]
    samples.append(
        {
            "nombre_participation_pee": int(quitter_row["nombre_participation_pee"]),
            "nb_formations_suivies": int(quitter_row["nb_formations_suivies"]),
            "nombre_employee_sous_responsabilite": int(
                quitter_row["nombre_employee_sous_responsabilite"]
            ),
            "distance_domicile_travail": int(quitter_row["distance_domicile_travail"]),
            "niveau_education": int(quitter_row["niveau_education"]),
            "domaine_etude": quitter_row["domaine_etude"],
            "ayant_enfants": quitter_row["ayant_enfants"],
            "frequence_deplacement": quitter_row["frequence_deplacement"],
            "annees_depuis_la_derniere_promotion": int(
                quitter_row["annees_depuis_la_derniere_promotion"]
            ),
            "annes_sous_responsable_actuel": int(
                quitter_row["annes_sous_responsable_actuel"]
            ),
            "satisfaction_employee_environnement": int(
                quitter_row["satisfaction_employee_environnement"]
            ),
            "note_evaluation_precedente": int(
                quitter_row["note_evaluation_precedente"]
            ),
            "niveau_hierarchique_poste": int(quitter_row["niveau_hierarchique_poste"]),
            "satisfaction_employee_nature_travail": int(
                quitter_row["satisfaction_employee_nature_travail"]
            ),
            "satisfaction_employee_equipe": int(
                quitter_row["satisfaction_employee_equipe"]
            ),
            "satisfaction_employee_equilibre_pro_perso": int(
                quitter_row["satisfaction_employee_equilibre_pro_perso"]
            ),
            "note_evaluation_actuelle": int(quitter_row["note_evaluation_actuelle"]),
            "heure_supplementaires": quitter_row["heure_supplementaires"],
            "augementation_salaire_precedente": float(
                quitter_row["augementation_salaire_precedente"].strip("%")
            ),
            "age": int(quitter_row["age"]),
            "genre": quitter_row["genre"],
            "revenu_mensuel": float(quitter_row["revenu_mensuel"]),
            "statut_marital": quitter_row["statut_marital"],
            "departement": quitter_row["departement"],
            "poste": quitter_row["poste"],
            "nombre_experiences_precedentes": int(
                quitter_row["nombre_experiences_precedentes"]
            ),
            "nombre_heures_travailless": int(quitter_row["nombre_heures_travailless"]),
            "annee_experience_totale": int(quitter_row["annee_experience_totale"]),
            "annees_dans_l_entreprise": int(quitter_row["annees_dans_l_entreprise"]),
            "annees_dans_le_poste_actuel": int(
                quitter_row["annees_dans_le_poste_actuel"]
            ),
        }
    )

    # Exemple 2: Employé qui reste (cas négatif)
    rester_row = df_merged[df_merged["a_quitte_l_entreprise"] == "Non"].iloc[0]
    samples.append(
        {
            "nombre_participation_pee": int(rester_row["nombre_participation_pee"]),
            "nb_formations_suivies": int(rester_row["nb_formations_suivies"]),
            "nombre_employee_sous_responsabilite": int(
                rester_row["nombre_employee_sous_responsabilite"]
            ),
            "distance_domicile_travail": int(rester_row["distance_domicile_travail"]),
            "niveau_education": int(rester_row["niveau_education"]),
            "domaine_etude": rester_row["domaine_etude"],
            "ayant_enfants": rester_row["ayant_enfants"],
            "frequence_deplacement": rester_row["frequence_deplacement"],
            "annees_depuis_la_derniere_promotion": int(
                rester_row["annees_depuis_la_derniere_promotion"]
            ),
            "annes_sous_responsable_actuel": int(
                rester_row["annes_sous_responsable_actuel"]
            ),
            "satisfaction_employee_environnement": int(
                rester_row["satisfaction_employee_environnement"]
            ),
            "note_evaluation_precedente": int(rester_row["note_evaluation_precedente"]),
            "niveau_hierarchique_poste": int(rester_row["niveau_hierarchique_poste"]),
            "satisfaction_employee_nature_travail": int(
                rester_row["satisfaction_employee_nature_travail"]
            ),
            "satisfaction_employee_equipe": int(
                rester_row["satisfaction_employee_equipe"]
            ),
            "satisfaction_employee_equilibre_pro_perso": int(
                rester_row["satisfaction_employee_equilibre_pro_perso"]
            ),
            "note_evaluation_actuelle": int(rester_row["note_evaluation_actuelle"]),
            "heure_supplementaires": rester_row["heure_supplementaires"],
            "augementation_salaire_precedente": float(
                rester_row["augementation_salaire_precedente"].strip("%")
            ),
            "age": int(rester_row["age"]),
            "genre": rester_row["genre"],
            "revenu_mensuel": float(rester_row["revenu_mensuel"]),
            "statut_marital": rester_row["statut_marital"],
            "departement": rester_row["departement"],
            "poste": rester_row["poste"],
            "nombre_experiences_precedentes": int(
                rester_row["nombre_experiences_precedentes"]
            ),
            "nombre_heures_travailless": int(rester_row["nombre_heures_travailless"]),
            "annee_experience_totale": int(rester_row["annee_experience_totale"]),
            "annees_dans_l_entreprise": int(rester_row["annees_dans_l_entreprise"]),
            "annees_dans_le_poste_actuel": int(
                rester_row["annees_dans_le_poste_actuel"]
            ),
        }
    )

    # Exemple 3: Cas limite - âge minimum
    jeune_row = df_merged[df_merged["age"] == df_merged["age"].min()].iloc[0]
    samples.append(
        {
            "nombre_participation_pee": int(jeune_row["nombre_participation_pee"]),
            "nb_formations_suivies": int(jeune_row["nb_formations_suivies"]),
            "nombre_employee_sous_responsabilite": int(
                jeune_row["nombre_employee_sous_responsabilite"]
            ),
            "distance_domicile_travail": int(jeune_row["distance_domicile_travail"]),
            "niveau_education": int(jeune_row["niveau_education"]),
            "domaine_etude": jeune_row["domaine_etude"],
            "ayant_enfants": jeune_row["ayant_enfants"],
            "frequence_deplacement": jeune_row["frequence_deplacement"],
            "annees_depuis_la_derniere_promotion": int(
                jeune_row["annees_depuis_la_derniere_promotion"]
            ),
            "annes_sous_responsable_actuel": int(
                jeune_row["annes_sous_responsable_actuel"]
            ),
            "satisfaction_employee_environnement": int(
                jeune_row["satisfaction_employee_environnement"]
            ),
            "note_evaluation_precedente": int(jeune_row["note_evaluation_precedente"]),
            "niveau_hierarchique_poste": int(jeune_row["niveau_hierarchique_poste"]),
            "satisfaction_employee_nature_travail": int(
                jeune_row["satisfaction_employee_nature_travail"]
            ),
            "satisfaction_employee_equipe": int(
                jeune_row["satisfaction_employee_equipe"]
            ),
            "satisfaction_employee_equilibre_pro_perso": int(
                jeune_row["satisfaction_employee_equilibre_pro_perso"]
            ),
            "note_evaluation_actuelle": int(jeune_row["note_evaluation_actuelle"]),
            "heure_supplementaires": jeune_row["heure_supplementaires"],
            "augementation_salaire_precedente": float(
                jeune_row["augementation_salaire_precedente"].strip("%")
            ),
            "age": int(jeune_row["age"]),
            "genre": jeune_row["genre"],
            "revenu_mensuel": float(jeune_row["revenu_mensuel"]),
            "statut_marital": jeune_row["statut_marital"],
            "departement": jeune_row["departement"],
            "poste": jeune_row["poste"],
            "nombre_experiences_precedentes": int(
                jeune_row["nombre_experiences_precedentes"]
            ),
            "nombre_heures_travailless": int(jeune_row["nombre_heures_travailless"]),
            "annee_experience_totale": int(jeune_row["annee_experience_totale"]),
            "annees_dans_l_entreprise": int(jeune_row["annees_dans_l_entreprise"]),
            "annees_dans_le_poste_actuel": int(
                jeune_row["annees_dans_le_poste_actuel"]
            ),
        }
    )

    return samples
