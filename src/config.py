#!/usr/bin/env python3
"""
Module de configuration de l'application.

Charge les variables d'environnement depuis .env et fournit
une interface pour accéder à la configuration de manière sécurisée.
"""
import os
from functools import lru_cache

from dotenv import load_dotenv

# Charger .env au démarrage du module
load_dotenv()


class Settings:
    """
    Configuration de l'application.

    Toutes les valeurs sensibles (API keys, etc.) sont chargées depuis
    les variables d'environnement ou le fichier .env.
    """

    # ===== SÉCURITÉ =====
    API_KEY: str = os.getenv("API_KEY", "dev-key-change-me-in-production")

    # ===== API =====
    API_VERSION: str = os.getenv("API_VERSION", "3.3.0")
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # ===== MODÈLE =====
    HF_MODEL_REPO: str = os.getenv(
        "HF_MODEL_REPO", "ASI-Engineer/employee-turnover-model"
    )
    MODEL_FILENAME: str = os.getenv("MODEL_FILENAME", "model/model.pkl")

    # ===== ENVIRONNEMENT =====
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ===== BASE DE DONNÉES =====
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://ml_user:15975359320@localhost:5432/oc_p5_db"
    )

    @property
    def is_api_key_required(self) -> bool:
        """
        Vérifie si l'API key est requise.

        Returns:
            False en mode DEBUG, True en production.
        """
        return not self.DEBUG


@lru_cache()
def get_settings() -> Settings:
    """
    Retourne l'instance singleton des settings.

    Le décorateur @lru_cache() assure qu'on ne crée qu'une seule instance.

    Returns:
        Settings: Configuration de l'application.
    """
    return Settings()
