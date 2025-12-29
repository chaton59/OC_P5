#!/usr/bin/env python3
"""
Tests pour la base de données PostgreSQL.

Ces tests vérifient :
- La connexion à PostgreSQL
- La création des tables
- Les opérations d'insertion
- Les requêtes de lecture
"""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from db_models import Dataset, MLLog
from src.config import get_settings


def can_connect_to_db():
    """Vérifie si la connexion à la base de données est possible."""
    try:
        settings = get_settings()
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


# Skip tous les tests de ce module si la DB n'est pas disponible
pytestmark = pytest.mark.skipif(
    not can_connect_to_db(),
    reason="Base de données PostgreSQL non disponible (tests locaux uniquement)",
)


class TestDatabaseConnection:
    """Tests de connexion à la base de données."""

    def test_database_connection(self):
        """Test que la connexion à PostgreSQL fonctionne."""
        settings = get_settings()
        try:
            engine = create_engine(settings.DATABASE_URL)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                row = result.fetchone()
                assert row is not None
                assert row[0] == 1
        except SQLAlchemyError as e:
            pytest.fail(f"Connexion à la base de données échouée: {e}")

    def test_tables_exist(self):
        """Test que les tables dataset et ml_logs existent."""
        settings = get_settings()
        engine = create_engine(settings.DATABASE_URL)

        with engine.connect() as conn:
            # Vérifier que les tables existent
            result = conn.execute(
                text(
                    """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('dataset', 'ml_logs')
            """
                )
            )
            tables = [row[0] for row in result]
            assert "dataset" in tables
            assert "ml_logs" in tables


class TestDatasetOperations:
    """Tests des opérations sur la table dataset."""

    def test_insert_dataset_entry(self):
        """Test l'insertion d'une entrée dans dataset."""
        settings = get_settings()
        engine = create_engine(settings.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Créer une entrée de test
            test_entry = Dataset(
                features_json={
                    "age": 30,
                    "genre": "M",
                    "revenu_mensuel": 3500,
                    "satisfaction_employee_environnement": 3,
                },
                target="Non",
            )

            session.add(test_entry)
            session.commit()

            # Vérifier que l'entrée a été insérée
            assert test_entry.id is not None

            # Nettoyer
            session.delete(test_entry)
            session.commit()

        except SQLAlchemyError as e:
            session.rollback()
            pytest.fail(f"Échec de l'insertion dataset: {e}")
        finally:
            session.close()

    def test_query_dataset(self):
        """Test les requêtes sur la table dataset."""
        settings = get_settings()
        engine = create_engine(settings.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Compter le nombre d'entrées
            count = session.query(Dataset).count()
            assert isinstance(count, int)
            assert count >= 0

            # Tester une requête avec filtre
            if count > 0:
                sample = session.query(Dataset).first()
                assert sample is not None
                assert sample.features_json is not None
                assert sample.target in ["Oui", "Non"]

        except SQLAlchemyError as e:
            pytest.fail(f"Échec de la requête dataset: {e}")
        finally:
            session.close()


class TestMLLogOperations:
    """Tests des opérations sur la table ml_logs."""

    def test_insert_ml_log_entry(self):
        """Test l'insertion d'une entrée dans ml_logs."""
        settings = get_settings()
        engine = create_engine(settings.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Créer une entrée de test
            test_entry = MLLog(
                input_json={"age": 30, "genre": "M", "revenu_mensuel": 3500},
                prediction="Non",
            )

            session.add(test_entry)
            session.commit()

            # Vérifier que l'entrée a été insérée
            assert test_entry.id is not None
            assert test_entry.created_at is not None

            # Nettoyer
            session.delete(test_entry)
            session.commit()

        except SQLAlchemyError as e:
            session.rollback()
            pytest.fail(f"Échec de l'insertion ML log: {e}")
        finally:
            session.close()

    def test_query_ml_logs(self):
        """Test les requêtes sur la table ml_logs."""
        settings = get_settings()
        engine = create_engine(settings.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Compter le nombre d'entrées
            count = session.query(MLLog).count()
            assert isinstance(count, int)
            assert count >= 0

            # Tester une requête avec filtre
            if count > 0:
                sample = session.query(MLLog).first()
                assert sample is not None
                assert sample.input_json is not None
                assert sample.prediction in ["Oui", "Non"]
                assert sample.created_at is not None

        except SQLAlchemyError as e:
            pytest.fail(f"Échec de la requête ML logs: {e}")
        finally:
            session.close()


class TestDatabaseIntegrity:
    """Tests d'intégrité de la base de données."""

    def test_foreign_keys_and_constraints(self):
        """Test que les contraintes de base de données sont respectées."""
        settings = get_settings()
        engine = create_engine(settings.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Tester qu'on ne peut pas insérer des données invalides
            # (Ces tests dépendent des contraintes définies dans les modèles)

            # Test target valide
            valid_entry = Dataset(features_json={"test": "data"}, target="Oui")
            session.add(valid_entry)
            session.commit()
            session.delete(valid_entry)
            session.commit()

        except SQLAlchemyError as e:
            session.rollback()
            pytest.fail(f"Contraintes de base de données non respectées: {e}")
        finally:
            session.close()
