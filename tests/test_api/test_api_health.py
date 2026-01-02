#!/usr/bin/env python3
"""
Tests pour l'endpoint /health de l'API.

Ces tests vérifient que l'endpoint de monitoring fonctionne correctement
et retourne les informations attendues sur l'état de l'API.
"""


def test_health_endpoint_status_code(client):
    """
    Test que /health retourne un code 200.

    Args:
        client: Fixture TestClient FastAPI.
    """
    response = client.get("/health")
    assert response.status_code == 200, "L'endpoint /health devrait retourner 200"


def test_health_endpoint_response_structure(client):
    """
    Test que /health retourne la structure JSON attendue.

    Args:
        client: Fixture TestClient FastAPI.
    """
    response = client.get("/health")
    data = response.json()

    # Vérifier les clés obligatoires
    assert "status" in data, "La réponse doit contenir 'status'"
    assert "model_loaded" in data, "La réponse doit contenir 'model_loaded'"
    assert "model_type" in data, "La réponse doit contenir 'model_type'"
    assert "version" in data, "La réponse doit contenir 'version'"


def test_health_endpoint_status_value(client):
    """
    Test que le status est 'healthy'.

    Args:
        client: Fixture TestClient FastAPI.
    """
    response = client.get("/health")
    data = response.json()

    assert data["status"] == "healthy", "Le status devrait être 'healthy'"


def test_health_endpoint_model_loaded(client):
    """
    Test que le modèle est chargé avec succès.

    Args:
        client: Fixture TestClient FastAPI.
    """
    response = client.get("/health")
    data = response.json()

    assert data["model_loaded"] is True, "Le modèle devrait être chargé"
    assert data["model_type"] == "Pipeline", "Le type devrait être 'Pipeline'"


def test_health_endpoint_version(client):
    """
    Test que la version est présente et au bon format.

    Args:
        client: Fixture TestClient FastAPI.
    """
    response = client.get("/health")
    data = response.json()

    assert "version" in data, "La version doit être présente"
    assert isinstance(data["version"], str), "La version doit être une string"
    assert len(data["version"]) > 0, "La version ne doit pas être vide"


def test_health_endpoint_content_type(client):
    """
    Test que le Content-Type est application/json.

    Args:
        client: Fixture TestClient FastAPI.
    """
    response = client.get("/health")
    assert "application/json" in response.headers["content-type"]
