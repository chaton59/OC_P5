#!/usr/bin/env python3
"""
Script de création de la base de données et des tables via SQLAlchemy.

Ce script utilise SQLAlchemy pour créer automatiquement la base de données
et les tables nécessaires pour le projet Employee Turnover.

Usage:
    poetry run python scripts/create_db.py

Tables créées:
    - dataset : Stockage des données d'entraînement (features_json, target)
    - ml_logs : Logs des prédictions de l'API (inputs, outputs, timestamps)
"""
from sqlalchemy import create_engine

from db_models import Base
from src.config import get_settings


def main():
    """Crée la base de données et toutes les tables."""
    print("🔧 Création de la base de données...")

    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)

    # Création de toutes les tables
    Base.metadata.create_all(engine)

    print("✅ Base de données et tables créées avec succès !")
    print("📊 Tables créées :")
    print("   - dataset : Stockage des données d'entraînement")
    print("   - ml_logs : Logs des prédictions de l'API")
    print("\n💡 Prochaine étape : Insérer les données avec insert_dataset.py")


if __name__ == "__main__":
    main()

