#!/usr/bin/env python3
"""
Script de test des modèles SQLAlchemy pour la base de données PostgreSQL.

Ce script teste la création des tables et l'insertion de données d'exemple.
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données (pour test local)
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://ml_user:15975359320@localhost:5432/oc_p5_db"
)

# Importer les modèles
Base = declarative_base()


class Dataset(Base):
    __tablename__ = "dataset"
    id = Column(Integer, primary_key=True)
    features_json = Column(JSON)  # Features from sondage, eval, sirh data
    target = Column(String)  # Target: 'Oui' or 'Non' for turnover


class MLLog(Base):
    __tablename__ = "ml_logs"
    id = Column(Integer, primary_key=True)
    input_json = Column(JSON)  # Inputs flexibles (JSON for features variables)
    prediction = Column(String)  # Output ML ('Oui' or 'Non')
    created_at = Column(DateTime, default=func.now())  # Timestamp auto pour traçabilité


def test_database_connection():
    """Test de connexion à la base de données."""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect():
            print("✅ Connexion à PostgreSQL réussie")
        return engine
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None


def create_tables(engine):
    """Création des tables."""
    try:
        Base.metadata.create_all(engine)
        print("✅ Tables créées avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        return False


def test_insert_data(engine):
    """Test d'insertion de données d'exemple."""
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # Exemple de données dataset
        sample_dataset = Dataset(
            features_json={
                "age": 35,
                "genre": "M",
                "revenu_mensuel": 4500,
                "satisfaction_employee_environnement": 3,
            },
            target="Non",
        )

        # Exemple de log ML
        sample_log = MLLog(
            input_json={
                "age": 35,
                "genre": "M",
                "revenu_mensuel": 4500,
                "satisfaction_employee_environnement": 3,
            },
            prediction="Non",
        )

        session.add(sample_dataset)
        session.add(sample_log)
        session.commit()

        print("✅ Données d'exemple insérées avec succès")

        # Vérifier les données
        datasets = session.query(Dataset).all()
        logs = session.query(MLLog).all()

        print(f"📊 Nombre d'enregistrements Dataset: {len(datasets)}")
        print(f"📊 Nombre d'enregistrements MLLog: {len(logs)}")

        session.close()
        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'insertion: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Test des modèles de base de données\n")

    # Test connexion
    engine = test_database_connection()
    if not engine:
        print("❌ Impossible de continuer sans connexion DB")
        exit(1)

    # Créer tables
    if not create_tables(engine):
        print("❌ Impossible de créer les tables")
        exit(1)

    # Tester insertion
    if not test_insert_data(engine):
        print("❌ Échec du test d'insertion")
        exit(1)

    print("\n🎉 Tous les tests passés avec succès !")
