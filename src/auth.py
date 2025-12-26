#!/usr/bin/env python3
"""
Module d'authentification pour l'API.

Fournit un système de vérification de clé API via header HTTP.
"""
from fastapi import Header, HTTPException, status
from fastapi.security import APIKeyHeader

from src.config import get_settings

# Schéma pour la documentation Swagger
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(x_api_key: str = Header(None)) -> str:
    """
    Vérifie que la clé API fournie est valide.

    Cette fonction est utilisée comme dépendance FastAPI (Depends).
    Elle vérifie le header HTTP "X-API-Key" et compare avec la clé configurée.

    Args:
        x_api_key: Clé API fournie dans le header HTTP.

    Returns:
        str: La clé API validée.

    Raises:
        HTTPException: 401 si la clé est manquante ou invalide.

    Comment ça marche :
        1. FastAPI extrait automatiquement le header "X-API-Key"
        2. La fonction compare avec la clé configurée dans .env
        3. Si valide → continue, sinon → erreur 401

    Exemple d'utilisation :
        ```python
        @app.post("/predict", dependencies=[Depends(verify_api_key)])
        async def predict(...):
            # Cette route est protégée !
        ```

    Exemple de requête curl :
        ```bash
        curl -X POST http://localhost:8000/predict \\
          -H "X-API-Key: your-secret-key" \\
          -H "Content-Type: application/json" \\
          -d '{...}'
        ```
    """
    settings = get_settings()

    # En mode DEBUG, on peut désactiver l'auth
    if settings.DEBUG:
        return "debug-mode-no-auth-required"

    # Vérifier que la clé est fournie
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "API Key missing",
                "message": "Le header 'X-API-Key' est requis pour accéder à cette ressource",
                "solution": "Ajoutez le header: -H 'X-API-Key: votre-cle-api'",
            },
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Vérifier que la clé est correcte
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Invalid API Key",
                "message": "La clé API fournie est invalide",
                "solution": "Vérifiez votre clé API ou contactez l'administrateur",
            },
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return x_api_key


def get_api_key_dependency():
    """
    Retourne la dépendance d'authentification si nécessaire.

    Permet de conditionner l'authentification selon la config.

    Returns:
        Depends(verify_api_key) si auth requise, None sinon.
    """
    settings = get_settings()
    if settings.is_api_key_required:
        from fastapi import Depends

        return Depends(verify_api_key)
    return None
