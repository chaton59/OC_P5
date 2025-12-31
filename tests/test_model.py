#!/usr/bin/env python3
"""
Tests unitaires pour les composants ML (modèle et preprocessing).

Ces tests vérifient les fonctions individuelles de chargement du modèle,
preprocessing des données, et validation Pydantic sans passer par l'API.
"""

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from src.models import get_model_info, load_model
from src.preprocessing import (
    create_input_dataframe,
    encode_and_scale,
    engineer_features,
    preprocess_for_prediction,
)
from src.schemas import EmployeeInput


class TestModelLoading:
    """Tests unitaires pour le chargement du modèle."""

    def test_load_model_returns_pipeline(self, monkeypatch):
        """Test que load_model retourne un objet Pipeline."""
        # Le mock est déjà configuré dans conftest.py
        model = load_model()
        assert model is not None
        assert hasattr(model, "predict")
        assert hasattr(model, "predict_proba")

    def test_get_model_info_structure(self, monkeypatch):
        """Test que get_model_info retourne la structure attendue."""
        info = get_model_info()

        required_keys = ["status", "model_type", "hf_hub_repo", "model_file", "cached"]
        for key in required_keys:
            assert key in info, f"Clé manquante: {key}"

        assert info["status"] == "✅ Modèle chargé"
        assert info["cached"] is True

    def test_model_predict_returns_correct_types(self, monkeypatch):
        """Test que les prédictions du modèle ont les bons types."""
        model = load_model()

        # Créer des données de test (format numpy array)
        X_test = np.array([[0.5] * 27])  # 27 features selon SCALER_PARAMS

        # Test predict
        predictions = model.predict(X_test)
        assert isinstance(predictions, np.ndarray)
        assert predictions.shape == (1,)
        assert predictions[0] in [0, 1]

        # Test predict_proba
        probabilities = model.predict_proba(X_test)
        assert isinstance(probabilities, np.ndarray)
        assert probabilities.shape == (1, 2)
        assert np.allclose(probabilities.sum(axis=1), 1.0)  # Probabilités somment à 1
        assert all(0 <= p <= 1 for p in probabilities.flatten())


class TestPreprocessing:
    """Tests unitaires pour les fonctions de preprocessing."""

    def test_create_input_dataframe_structure(self, valid_employee_data):
        """Test que create_input_dataframe crée un DataFrame avec les bonnes colonnes."""
        employee = EmployeeInput(**valid_employee_data)
        df = create_input_dataframe(employee)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

        # Vérifier que toutes les colonnes attendues sont présentes
        expected_columns = [
            "nombre_participation_pee",
            "nb_formations_suivies",
            "nombre_employee_sous_responsabilite",
            "distance_domicile_travail",
            "niveau_education",
            "domaine_etude",
            "ayant_enfants",
            "frequence_deplacement",
            "annees_depuis_la_derniere_promotion",
            "annes_sous_responsable_actuel",
            "satisfaction_employee_environnement",
            "note_evaluation_precedente",
            "niveau_hierarchique_poste",
            "satisfaction_employee_nature_travail",
            "satisfaction_employee_equipe",
            "satisfaction_employee_equilibre_pro_perso",
            "note_evaluation_actuelle",
            "heure_supplementaires",
            "augementation_salaire_precedente",
            "age",
            "genre",
            "revenu_mensuel",
            "statut_marital",
            "departement",
            "poste",
            "nombre_experiences_precedentes",
            "nombre_heures_travailless",
            "annee_experience_totale",
            "annees_dans_l_entreprise",
            "annees_dans_le_poste_actuel",
        ]

        for col in expected_columns:
            assert col in df.columns, f"Colonne manquante: {col}"

    def test_engineer_features_adds_new_columns(self, valid_employee_data):
        """Test que engineer_features ajoute les colonnes calculées."""
        employee = EmployeeInput(**valid_employee_data)
        df = create_input_dataframe(employee)
        df_engineered = engineer_features(df)

        # Vérifier que les nouvelles colonnes sont ajoutées
        new_columns = [
            "revenu_par_anciennete",
            "experience_par_anciennete",
            "satisfaction_moyenne",
            "promo_par_anciennete",
        ]

        for col in new_columns:
            assert col in df_engineered.columns, f"Nouvelle colonne manquante: {col}"

    def test_encode_and_scale_returns_dataframe(self, valid_employee_data):
        """Test que encode_and_scale retourne un DataFrame avec les bonnes dimensions."""
        employee = EmployeeInput(**valid_employee_data)
        df = create_input_dataframe(employee)
        df_engineered = engineer_features(df)
        df_encoded = encode_and_scale(df_engineered)

        assert isinstance(df_encoded, pd.DataFrame)
        assert len(df_encoded) == 1
        # Doit avoir 50 colonnes selon le preprocessing réel
        assert df_encoded.shape[1] == 50

    def test_preprocess_for_prediction_full_pipeline(self, valid_employee_data):
        """Test que preprocess_for_prediction applique tout le pipeline."""
        employee = EmployeeInput(**valid_employee_data)
        result = preprocess_for_prediction(employee)

        assert isinstance(result, np.ndarray)
        assert result.shape[1] == 50  # 50 features selon le preprocessing réel

    def test_preprocessing_with_edge_cases(self, sample_dataset_rows):
        """Test le preprocessing avec des données réelles variées."""
        for i, employee_data in enumerate(sample_dataset_rows):
            # Le code ne devrait pas lever d'exception avec des données valides
            employee = EmployeeInput(**employee_data)
            result = preprocess_for_prediction(employee)
            assert isinstance(result, np.ndarray)
            assert result.shape[1] == 50


class TestPydanticValidation:
    """Tests unitaires pour la validation Pydantic (sans API)."""

    def test_employee_input_valid_data(self, valid_employee_data):
        """Test que EmployeeInput accepte les données valides."""
        employee = EmployeeInput(**valid_employee_data)
        assert employee.age == valid_employee_data["age"]
        assert employee.genre == valid_employee_data["genre"]

    def test_employee_input_missing_fields(self):
        """Test que EmployeeInput rejette les données avec champs manquants."""
        incomplete_data = {"age": 30, "genre": "M"}

        with pytest.raises(ValidationError) as exc_info:
            EmployeeInput(**incomplete_data)

        assert "missing" in str(exc_info.value)

    def test_employee_input_invalid_types(self, valid_employee_data):
        """Test que EmployeeInput rejette les mauvais types."""
        invalid_data = valid_employee_data.copy()
        invalid_data["age"] = "trente"  # String au lieu d'int

        with pytest.raises(ValidationError) as exc_info:
            EmployeeInput(**invalid_data)

        assert "unable to parse string as an integer" in str(exc_info.value)

    def test_employee_input_negative_values(self, valid_employee_data):
        """Test que EmployeeInput rejette les valeurs négatives invalides."""
        invalid_data = valid_employee_data.copy()
        invalid_data["age"] = -5

        with pytest.raises(ValidationError) as exc_info:
            EmployeeInput(**invalid_data)

        assert "greater than or equal to 18" in str(exc_info.value)

    def test_employee_input_invalid_enum_values(self, valid_employee_data):
        """Test que EmployeeInput rejette les valeurs enum invalides."""
        invalid_data = valid_employee_data.copy()
        invalid_data["genre"] = "X"  # Genre invalide

        with pytest.raises(ValidationError) as exc_info:
            EmployeeInput(**invalid_data)

        assert "Input should be 'M' or 'F'" in str(exc_info.value)

    def test_employee_input_age_limits(self, valid_employee_data):
        """Test les limites d'âge."""
        # Test âge minimum
        min_age_data = valid_employee_data.copy()
        min_age_data["age"] = 18
        employee = EmployeeInput(**min_age_data)  # Devrait passer
        assert employee.age == 18

        # Test âge trop jeune
        invalid_data = valid_employee_data.copy()
        invalid_data["age"] = 17
        with pytest.raises(ValidationError):
            EmployeeInput(**invalid_data)

        # Test âge trop vieux
        invalid_data = valid_employee_data.copy()
        invalid_data["age"] = 66
        with pytest.raises(ValidationError):
            EmployeeInput(**invalid_data)

    def test_employee_input_revenue_limits(self, valid_employee_data):
        """Test les limites de revenu."""
        # Test revenu trop bas
        invalid_data = valid_employee_data.copy()
        invalid_data["revenu_mensuel"] = 999
        with pytest.raises(ValidationError):
            EmployeeInput(**invalid_data)

    def test_employee_input_formation_limits(self, valid_employee_data):
        """Test les limites du nombre de formations."""
        # Test nombre de formations trop élevé
        invalid_data = valid_employee_data.copy()
        invalid_data["nb_formations_suivies"] = 11
        with pytest.raises(ValidationError):
            EmployeeInput(**invalid_data)


class TestModelIntegration:
    """Tests d'intégration entre preprocessing et modèle."""

    def test_full_prediction_pipeline(self, valid_employee_data):
        """Test le pipeline complet : validation -> preprocessing -> prédiction."""
        # 1. Validation Pydantic
        employee = EmployeeInput(**valid_employee_data)

        # 2. Preprocessing
        X = preprocess_for_prediction(employee)

        # 3. Prédiction
        model = load_model()
        prediction = model.predict(X)
        probabilities = model.predict_proba(X)

        # Vérifications
        assert isinstance(prediction, np.ndarray)
        assert isinstance(probabilities, np.ndarray)
        assert prediction[0] in [0, 1]
        assert probabilities.shape == (1, 2)
        assert abs(probabilities.sum() - 1.0) < 1e-6

    def test_prediction_consistency(self, valid_employee_data):
        """Test que les prédictions sont consistantes pour les mêmes données."""
        employee = EmployeeInput(**valid_employee_data)
        X = preprocess_for_prediction(employee)
        model = load_model()

        # Faire plusieurs prédictions
        predictions = []
        probabilities = []

        for _ in range(5):
            pred = model.predict(X)
            prob = model.predict_proba(X)
            predictions.append(pred[0])
            probabilities.append(prob[0])

        # Toutes les prédictions devraient être identiques
        assert all(p == predictions[0] for p in predictions)
        assert all(np.allclose(p, probabilities[0]) for p in probabilities)


class TestHuggingFaceIntegration:
    """Tests d'intégration avec l'API Hugging Face (optionnels - nécessitent connexion internet)."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_model_loading_from_hf_hub(self):
        """Test le chargement réel du modèle depuis HF Hub (nécessite connexion internet)."""
        # Forcer le rechargement pour tester HF Hub
        import src.models
        src.models._model_cache = None  # Reset cache

        try:
            model = load_model(force_reload=True)
            assert model is not None
            assert hasattr(model, "predict")
            assert hasattr(model, "predict_proba")

            # Tester une prédiction réelle
            X_test = np.array([[0.5] * 50])  # 50 features
            prediction = model.predict(X_test)
            probabilities = model.predict_proba(X_test)

            assert isinstance(prediction, np.ndarray)
            assert isinstance(probabilities, np.ndarray)
            assert prediction[0] in [0, 1]
            assert probabilities.shape == (1, 2)
            assert abs(probabilities.sum() - 1.0) < 1e-6

        finally:
            # Remettre le cache à None pour les autres tests
            src.models._model_cache = None

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_model_info_from_hf_hub(self):
        """Test les informations du modèle réel depuis HF Hub."""
        import src.models
        src.models._model_cache = None  # Reset cache

        try:
            info = get_model_info()

            required_keys = ["status", "model_type", "hf_hub_repo", "model_file", "cached"]
            for key in required_keys:
                assert key in info, f"Clé manquante: {key}"

            assert info["status"] == "✅ Modèle chargé"
            assert info["hf_hub_repo"] == "ASI-Engineer/employee-turnover-model"
            assert info["model_file"] == "model/model.pkl"
            assert info["cached"] is False  # Pas en cache lors du premier chargement

        finally:
            src.models._model_cache = None

    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_pipeline_with_real_model(self, valid_employee_data):
        """Test le pipeline complet avec le modèle réel depuis HF."""
        import src.models
        src.models._model_cache = None  # Reset cache

        try:
            # 1. Validation Pydantic
            employee = EmployeeInput(**valid_employee_data)

            # 2. Preprocessing
            X = preprocess_for_prediction(employee)

            # 3. Chargement modèle réel
            model = load_model(force_reload=True)

            # 4. Prédiction avec modèle réel
            prediction = model.predict(X)
            probabilities = model.predict_proba(X)

            # Vérifications
            assert isinstance(prediction, np.ndarray)
            assert isinstance(probabilities, np.ndarray)
            assert prediction[0] in [0, 1]
            assert probabilities.shape == (1, 2)
            assert abs(probabilities.sum() - 1.0) < 1e-6

            # Les probabilités devraient être différentes du mock (qui retourne toujours 0.5)
            # Vérifier que les probabilités ne sont pas exactement 0.5 (cas du mock)
            assert not np.allclose(probabilities, [[0.5, 0.5]], atol=0.01)

        finally:
            src.models._model_cache = None
