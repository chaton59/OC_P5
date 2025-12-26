#!/usr/bin/env python3
"""
Module de rate limiting pour protéger l'API contre les abus.

Utilise SlowAPI pour limiter le nombre de requêtes par IP/utilisateur.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import get_settings

settings = get_settings()

# Créer le limiter avec stratégie par IP
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"] if not settings.DEBUG else [],
    storage_uri="memory://",  # En production: utiliser Redis
    strategy="fixed-window",
)


def get_rate_limit_key(request):
    """
    Fonction pour obtenir la clé de rate limiting.

    En production, on pourrait utiliser l'API Key au lieu de l'IP.

    Args:
        request: Requête FastAPI.

    Returns:
        Clé unique pour identifier l'utilisateur.
    """
    # Priorité: API Key > IP
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"

    return get_remote_address(request)
