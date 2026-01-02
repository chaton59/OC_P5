#!/usr/bin/env python3
"""
Module de chargement et gestion du modèle MLflow.

Ce module encapsule la logique de chargement du modèle depuis Hugging Face Hub
via MLflow, avec gestion des erreurs et versioning.
"""
from typing import Any, Optional

from fastapi import HTTPException
from huggingface_hub import hf_hub_download

# Configuration
HF_MODEL_REPO = "ASI-Engineer/employee-turnover-model"
MODEL_FILENAME = "model/model.pkl"

# Cache global du modèle
_model_cache: Optional[Any] = None


def load_model(force_reload: bool = False) -> Any:
    """
    Charge le modèle depuis Hugging Face Hub via MLflow.

    Cette fonction implémente un système de cache pour éviter de recharger
    le modèle à chaque appel. Le modèle est chargé une seule fois au démarrage
    de l'application et mis en cache.

    Args:
        force_reload: Si True, force le rechargement du modèle même s'il est en cache.

    Returns:
        Le modèle MLflow chargé et prêt pour l'inférence.

    Raises:
        HTTPException: 500 si le modèle ne peut pas être chargé.

    Examples:
        >>> model = load_model()
        >>> # Utiliser le modèle pour prédiction
        >>> predictions = model.predict(X)
    """
    global _model_cache

    # Retourner le modèle en cache si disponible
    if _model_cache is not None and not force_reload:
        return _model_cache

    try:
        import joblib
        import logging

        logger = logging.getLogger(__name__)

        logger.info(f"🔄 Chargement du modèle depuis HF Hub: {HF_MODEL_REPO}")

        # Télécharger le modèle depuis Hugging Face Hub avec timeout
        try:
            model_path = hf_hub_download(
                repo_id=HF_MODEL_REPO,
                filename=MODEL_FILENAME,
                repo_type="model",
                timeout=60,  # Timeout de 60 secondes
            )
        except Exception as download_error:
            logger.error(f"Erreur téléchargement HF Hub: {download_error}")
            raise

        logger.info(f"📦 Modèle téléchargé: {model_path}")

        # Charger le modèle avec joblib
        model = joblib.load(model_path)

        # Mettre en cache
        _model_cache = model

        logger.info(f"✅ Modèle chargé avec succès: {type(model).__name__}")
        return model

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        error_msg = f"❌ Erreur lors du chargement du modèle: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Model loading failed",
                "message": str(e),
                "model_repo": HF_MODEL_REPO,
                "solution": "Vérifiez que le modèle est disponible sur HF Hub et correctement entraîné",
            },
        )


def get_model_info() -> dict:
    """
    Retourne les informations sur le modèle chargé.

    Returns:
        Dict contenant les métadonnées du modèle.

    Raises:
        HTTPException: 500 si le modèle n'est pas chargé.
    """
    try:
        model = load_model()

        return {
            "status": "✅ Modèle chargé",
            "model_type": type(model).__name__,
            "hf_hub_repo": HF_MODEL_REPO,
            "model_file": MODEL_FILENAME,
            "cached": _model_cache is not None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Model info unavailable", "message": str(e)},
        )


def load_preprocessing_artifacts(run_id: str) -> dict:
    """
    Charge les artifacts de preprocessing (scaler, encoders) depuis MLflow.

    Args:
        run_id: ID du run MLflow contenant les artifacts.

    Returns:
        Dict contenant les artifacts de preprocessing.

    Raises:
        HTTPException: 500 si les artifacts ne peuvent pas être chargés.

    Note:
        Cette fonction sera implémentée quand les preprocessing artifacts
        seront disponibles dans le modèle HF Hub.
    """
    raise NotImplementedError(
        "Le chargement des preprocessing artifacts sera implémenté "
        "lors de l'intégration complète avec MLflow"
    )


if __name__ == "__main__":
    # Test de chargement du modèle
    print("=" * 80)
    print("TEST DE CHARGEMENT DU MODÈLE")
    print("=" * 80)

    try:
        model = load_model()
        print("\n✅ Test réussi!")
        print(f"Type de modèle: {type(model).__name__}")

        # Afficher les infos
        info = get_model_info()
        print("\nInformations du modèle:")
        for key, value in info.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"\n❌ Test échoué: {e}")
