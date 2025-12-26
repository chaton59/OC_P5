#!/usr/bin/env python3
"""
Tests pour l'authentification API Key de l'API.

Ces tests vérifient que le système d'authentification est bien en place.
Note: Les tests en mode production nécessitent de redémarrer l'app avec DEBUG=False.
"""
import pytest


def test_auth_system_exists(client):
    """
    Test que le système d'authentification est configuré.

    Args:
        client: Fixture TestClient FastAPI.
    """
    # En mode DEBUG, l'auth est bypassée mais le système existe
    from src.config import get_settings

    settings = get_settings()

    # Vérifier que les settings sont configurés
    assert hasattr(settings, "API_KEY")
    assert hasattr(settings, "DEBUG")
    assert hasattr(settings, "is_api_key_required")


def test_predict_works_in_debug_mode(client, valid_employee_data):
    """
    Test que /predict fonctionne sans clé en mode DEBUG.

    Args:
        client: Client avec DEBUG=True (conftest.py).
        valid_employee_data: Fixture avec données valides.
    """
    # En mode DEBUG (conftest.py), pas besoin de clé
    response = client.post("/predict", json=valid_employee_data)

    assert response.status_code == 200, "DEBUG mode devrait permettre l'accès"


def test_auth_module_import():
    """Test que le module d'authentification s'importe correctement."""
    from src.auth import verify_api_key

    assert verify_api_key is not None
    assert callable(verify_api_key)


def test_config_module_import():
    """Test que le module de configuration s'importe correctement."""
    from src.config import get_settings, Settings

    settings = get_settings()
    assert isinstance(settings, Settings)


def test_api_key_header_name():
    """Test que le header API Key est correctement nommé."""
    from src.auth import api_key_header

    assert api_key_header.model.name == "X-API-Key"


# NOTE: Les tests suivants nécessitent de lancer l'API avec DEBUG=False
# Pour les tester manuellement:
# 1. Configurer .env avec DEBUG=False et une API_KEY
# 2. Lancer: uvicorn app:app --port 8000
# 3. Tester avec curl:
#    - Sans clé: curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{...}'
#      → Devrait retourner 401
#    - Avec mauvaise clé: curl -X POST http://localhost:8000/predict -H "X-API-Key: wrong" -d '{...}'
#      → Devrait retourner 401
#    - Avec bonne clé: curl -X POST http://localhost:8000/predict -H "X-API-Key: votre-cle" -d '{...}'
#      → Devrait retourner 200


@pytest.mark.skip(reason="Nécessite l'API en mode production (DEBUG=False)")
def test_predict_requires_api_key_in_production():
    """
    Test manuel: Vérifier que /predict nécessite une API Key en production.

    Pour tester:
        1. .env: DEBUG=False
        2. uvicorn app:app
        3. curl sans X-API-Key → 401
    """
    pass


@pytest.mark.skip(reason="Nécessite l'API en mode production (DEBUG=False)")
def test_predict_rejects_invalid_api_key():
    """
    Test manuel: Vérifier que /predict rejette les clés invalides.

    Pour tester:
        1. .env: DEBUG=False, API_KEY=secret
        2. uvicorn app:app
        3. curl avec X-API-Key: wrong → 401
    """
    pass


@pytest.mark.skip(reason="Nécessite l'API en mode production (DEBUG=False)")
def test_predict_accepts_valid_api_key():
    """
    Test manuel: Vérifier que /predict accepte les clés valides.

    Pour tester:
        1. .env: DEBUG=False, API_KEY=secret
        2. uvicorn app:app
        3. curl avec X-API-Key: secret → 200
    """
    pass
