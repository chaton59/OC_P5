#!/usr/bin/env python3
"""
Tests pour la validation des données d'entrée de l'API.

Ces tests vérifient que Pydantic valide correctement les données
et retourne des erreurs 422 avec des messages clairs.
"""
import pytest


def test_predict_missing_required_fields(client):
    """
    Test que l'API rejette les requêtes avec champs manquants.

    Args:
        client: Fixture TestClient FastAPI.
    """
    incomplete_data = {
        "age": 30,
        "genre": "M",
        # Manque tous les autres champs requis
    }

    response = client.post("/predict", json=incomplete_data)

    assert response.status_code == 422, "Devrait retourner 422 (Validation Error)"


def test_predict_invalid_field_types(client, valid_employee_data):
    """
    Test que l'API rejette les types de données incorrects.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    invalid_data = valid_employee_data.copy()
    invalid_data["age"] = "trente"  # String au lieu d'int

    response = client.post("/predict", json=invalid_data)

    assert response.status_code == 422


def test_predict_negative_values(client, valid_employee_data):
    """
    Test que l'API rejette les valeurs négatives invalides.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    invalid_data = valid_employee_data.copy()
    invalid_data["nombre_participation_pee"] = -1

    response = client.post("/predict", json=invalid_data)

    assert response.status_code == 422


def test_predict_age_too_young(client, valid_employee_data):
    """
    Test que l'API rejette les âges < 18 ans.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    invalid_data = valid_employee_data.copy()
    invalid_data["age"] = 15

    response = client.post("/predict", json=invalid_data)

    assert response.status_code == 422


def test_predict_age_too_old(client, valid_employee_data):
    """
    Test que l'API rejette les âges > 70 ans.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    invalid_data = valid_employee_data.copy()
    invalid_data["age"] = 75

    response = client.post("/predict", json=invalid_data)

    assert response.status_code == 422


def test_predict_invalid_genre(client, valid_employee_data):
    """
    Test que l'API rejette les genres invalides.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    invalid_data = valid_employee_data.copy()
    invalid_data["genre"] = "X"

    response = client.post("/predict", json=invalid_data)

    assert response.status_code == 422


def test_predict_invalid_departement(client, valid_employee_data):
    """
    Test que l'API rejette les départements invalides.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    invalid_data = valid_employee_data.copy()
    invalid_data["departement"] = "InvalidDept"

    response = client.post("/predict", json=invalid_data)

    assert response.status_code == 422


def test_predict_invalid_statut_marital(client, valid_employee_data):
    """
    Test que l'API rejette les statuts maritaux invalides.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    invalid_data = valid_employee_data.copy()
    invalid_data["statut_marital"] = "Pacsé"

    response = client.post("/predict", json=invalid_data)

    assert response.status_code == 422


def test_predict_invalid_frequence_deplacement(client, valid_employee_data):
    """
    Test que l'API rejette les fréquences de déplacement invalides.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    invalid_data = valid_employee_data.copy()
    invalid_data["frequence_deplacement"] = "Jamais"

    response = client.post("/predict", json=invalid_data)

    assert response.status_code == 422


def test_predict_error_response_structure(client, invalid_employee_data):
    """
    Test que les erreurs de validation ont la structure attendue.

    Args:
        client: Fixture TestClient FastAPI.
        invalid_employee_data: Fixture avec données invalides.
    """
    response = client.post("/predict", json=invalid_employee_data)

    assert response.status_code == 422
    data = response.json()

    # FastAPI retourne une structure 'detail' avec les erreurs
    assert "detail" in data, "La réponse d'erreur doit contenir 'detail'"


def test_predict_empty_json(client):
    """
    Test que l'API rejette un JSON vide.

    Args:
        client: Fixture TestClient FastAPI.
    """
    response = client.post("/predict", json={})

    assert response.status_code == 422


def test_predict_revenu_too_low(client, valid_employee_data):
    """
    Test que l'API rejette les revenus < 1000€.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    invalid_data = valid_employee_data.copy()
    invalid_data["revenu_mensuel"] = 500.0

    response = client.post("/predict", json=invalid_data)

    assert response.status_code == 422


def test_predict_nb_formations_out_of_range(client, valid_employee_data):
    """
    Test que l'API rejette nb_formations > 10.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    invalid_data = valid_employee_data.copy()
    invalid_data["nb_formations_suivies"] = 99

    response = client.post("/predict", json=invalid_data)

    assert response.status_code == 422
