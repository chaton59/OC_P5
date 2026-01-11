#!/usr/bin/env python3
"""
Tests des scénarios d'échec de la base de données.

Objectif: augmenter la couverture en validant la gestion d'erreurs
lorsque la connexion à la BDD échoue pendant le logging des prédictions.
"""
import pytest
from sqlalchemy.exc import SQLAlchemyError


@pytest.mark.usefixtures("client", "valid_employee_data")
def test_predict_handles_db_logging_failure_gracefully(client, valid_employee_data, monkeypatch):
    """
    Simule une erreur de connexion BDD lors du logging et vérifie
    que l'endpoint `/predict` continue de répondre sans planter.
    """
    # Forcer create_engine utilisé par l'API à lever une erreur
    def mock_create_engine_error(*args, **kwargs):
        raise SQLAlchemyError("Connection lost")

    monkeypatch.setattr("api.create_engine", mock_create_engine_error)

    # Appeler l'API: la prédiction doit réussir même si le logging BDD échoue
    response = client.post("/predict", json=valid_employee_data)

    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "probability_0" in data
    assert "probability_1" in data
    assert "risk_level" in data
