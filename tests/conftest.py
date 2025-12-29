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
os.environ["DEBUG"] = "True"
os.environ["API_KEY"] = "test-api-key-12345"

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
