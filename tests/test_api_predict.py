#!/usr/bin/env python3
"""
Tests pour l'endpoint /predict de l'API.

Ces tests vérifient que les prédictions fonctionnent correctement
avec des données valides et retournent le format attendu.
"""
import pytest


def test_predict_endpoint_with_valid_data(client, valid_employee_data):
    """
    Test que /predict fonctionne avec des données valides.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    response = client.post("/predict", json=valid_employee_data)

    assert response.status_code == 200, "Devrait retourner 200 avec données valides"


def test_predict_response_structure(client, valid_employee_data):
    """
    Test que la réponse contient tous les champs attendus.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    response = client.post("/predict", json=valid_employee_data)
    data = response.json()

    # Vérifier les clés obligatoires
    assert "prediction" in data, "La réponse doit contenir 'prediction'"
    assert "probability_0" in data, "La réponse doit contenir 'probability_0'"
    assert "probability_1" in data, "La réponse doit contenir 'probability_1'"
    assert "risk_level" in data, "La réponse doit contenir 'risk_level'"


def test_predict_prediction_values(client, valid_employee_data):
    """
    Test que la prédiction est 0 ou 1.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    response = client.post("/predict", json=valid_employee_data)
    data = response.json()

    assert data["prediction"] in [0, 1], "La prédiction doit être 0 ou 1"


def test_predict_probabilities_sum_to_one(client, valid_employee_data):
    """
    Test que les probabilités somment à ~1.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    response = client.post("/predict", json=valid_employee_data)
    data = response.json()

    prob_sum = data["probability_0"] + data["probability_1"]
    assert abs(prob_sum - 1.0) < 0.01, "Les probabilités doivent sommer à 1"


def test_predict_probabilities_range(client, valid_employee_data):
    """
    Test que les probabilités sont entre 0 et 1.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    response = client.post("/predict", json=valid_employee_data)
    data = response.json()

    assert 0 <= data["probability_0"] <= 1, "probability_0 doit être entre 0 et 1"
    assert 0 <= data["probability_1"] <= 1, "probability_1 doit être entre 0 et 1"


def test_predict_risk_level_values(client, valid_employee_data):
    """
    Test que risk_level est une valeur valide.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    response = client.post("/predict", json=valid_employee_data)
    data = response.json()

    valid_levels = ["Low", "Medium", "High"]
    assert (
        data["risk_level"] in valid_levels
    ), f"risk_level doit être dans {valid_levels}"


def test_predict_high_risk_employee(client, high_risk_employee_data):
    """
    Test avec un employé à haut risque de départ.

    Args:
        client: Fixture TestClient FastAPI.
        high_risk_employee_data: Fixture avec données haut risque.
    """
    response = client.post("/predict", json=high_risk_employee_data)
    data = response.json()

    assert response.status_code == 200
    # Note: On ne peut pas garantir prediction=1 (dépend du modèle)
    # Mais on vérifie que ça fonctionne
    assert "prediction" in data


def test_predict_content_type(client, valid_employee_data):
    """
    Test que le Content-Type est application/json.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    response = client.post("/predict", json=valid_employee_data)
    assert "application/json" in response.headers["content-type"]


def test_predict_consistency(client, valid_employee_data):
    """
    Test que les mêmes données produisent la même prédiction.

    Args:
        client: Fixture TestClient FastAPI.
        valid_employee_data: Fixture avec données valides.
    """
    response1 = client.post("/predict", json=valid_employee_data)
    response2 = client.post("/predict", json=valid_employee_data)

    data1 = response1.json()
    data2 = response2.json()

    assert (
        data1["prediction"] == data2["prediction"]
    ), "Prédictions doivent être identiques"
    assert abs(data1["probability_0"] - data2["probability_0"]) < 0.001
    assert abs(data1["probability_1"] - data2["probability_1"]) < 0.001
