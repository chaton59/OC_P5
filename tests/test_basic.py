"""Tests basiques pour le pipeline ML."""

from pathlib import Path


def test_pipeline_placeholder():
    """Test basique pour CI/CD."""
    assert True


def test_data_files_exist():
    """Vérifie que les fichiers de données existent."""
    data_dir = Path("data")
    assert (data_dir / "extrait_sondage.csv").exists()
    assert (data_dir / "extrait_eval.csv").exists()
    assert (data_dir / "extrait_sirh.csv").exists()


def test_preprocess_imports():
    """Vérifie que les imports ML fonctionnent."""
    from ml_model.preprocess import load_raw_data, preprocess_data

    assert preprocess_data is not None
    assert load_raw_data is not None


def test_train_imports():
    """Vérifie que le module d'entraînement s'importe."""
    from ml_model.train_model import train_model

    assert train_model is not None
