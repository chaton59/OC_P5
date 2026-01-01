#!/usr/bin/env python3
"""
Module de logging structuré pour l'API Employee Turnover.

Fournit un système de logging centralisé avec :
- Logs structurés en JSON
- Rotation automatique des fichiers
- Niveaux de log configurables
- Intégration FastAPI
"""
import logging
import sys
from pathlib import Path
from typing import Any, Dict

from pythonjsonlogger.jsonlogger import JsonFormatter

from src.config import get_settings

settings = get_settings()

# Créer le dossier logs s'il n'existe pas
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Fichiers de logs
LOG_FILE = LOG_DIR / "api.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"


class CustomJsonFormatter(JsonFormatter):
    """
    Formatter JSON personnalisé avec champs supplémentaires.
    """

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """
        Ajoute des champs personnalisés aux logs JSON.
        """
        super().add_fields(log_record, record, message_dict)

        # Ajouter des métadonnées
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # Timestamp ISO 8601
        if not log_record.get("timestamp"):
            log_record["timestamp"] = self.formatTime(record, self.datefmt)


def setup_logger(name: str = "employee_turnover_api") -> logging.Logger:
    """
    Configure et retourne un logger structuré.

    Args:
        name: Nom du logger.

    Returns:
        Logger configuré avec handlers console et fichiers.

    Examples:
        >>> logger = setup_logger()
        >>> logger.info("API démarrée", extra={"version": "2.0.0"})
    """
    logger = logging.getLogger(name)

    # Éviter duplication si déjà configuré
    if logger.handlers:
        return logger

    # Niveau de log depuis configuration
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # === HANDLER CONSOLE (stdout) ===
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Format simple pour la console en dev, JSON en prod
    if settings.DEBUG:
        console_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        console_format = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )

    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # === HANDLER FICHIER (tous les logs) ===
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(
        CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
    )
    logger.addHandler(file_handler)

    # === HANDLER ERREURS UNIQUEMENT ===
    error_handler = logging.FileHandler(ERROR_LOG_FILE, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
    )
    logger.addHandler(error_handler)

    # Éviter propagation au root logger
    logger.propagate = False

    return logger


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **kwargs: Any,
) -> None:
    """
    Log une requête HTTP avec métadonnées.

    Args:
        method: Méthode HTTP (GET, POST...).
        path: Chemin de l'endpoint.
        status_code: Code de statut HTTP.
        duration_ms: Durée de la requête en millisecondes.
        **kwargs: Métadonnées additionnelles.

    Examples:
        >>> log_request("POST", "/predict", 200, 45.3, user_id="123")
    """
    logger = logging.getLogger("employee_turnover_api")

    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
        **kwargs,
    }

    # Niveau selon status code
    if status_code >= 500:
        logger.error(f"Request {method} {path}", extra=log_data)
    elif status_code >= 400:
        logger.warning(f"Request {method} {path}", extra=log_data)
    else:
        logger.info(f"Request {method} {path}", extra=log_data)


def log_prediction(
    employee_id: str | None,
    prediction: int,
    probability: float,
    risk_level: str,
    duration_ms: float,
) -> None:
    """
    Log une prédiction effectuée.

    Args:
        employee_id: ID de l'employé (optionnel).
        prediction: Prédiction (0 ou 1).
        probability: Probabilité de turnover.
        risk_level: Niveau de risque ("low", "medium", "high").
        duration_ms: Durée du preprocessing + prédiction.

    Examples:
        >>> log_prediction("EMP123", 1, 0.87, "high", 23.4)
    """
    logger = logging.getLogger("employee_turnover_api")

    logger.info(
        "Prediction made",
        extra={
            "employee_id": employee_id,
            "prediction": prediction,
            "probability": round(probability, 4),
            "risk_level": risk_level,
            "duration_ms": round(duration_ms, 2),
        },
    )


def log_model_load(model_type: str, duration_ms: float, success: bool) -> None:
    """
    Log le chargement du modèle.

    Args:
        model_type: Type de modèle chargé.
        duration_ms: Durée du chargement.
        success: Si le chargement a réussi.

    Examples:
        >>> log_model_load("XGBoost Pipeline", 1234.5, True)
    """
    logger = logging.getLogger("employee_turnover_api")

    log_data = {
        "model_type": model_type,
        "duration_ms": round(duration_ms, 2),
        "success": success,
    }

    if success:
        logger.info("Model loaded successfully", extra=log_data)
    else:
        logger.error("Model loading failed", extra=log_data)


# Créer le logger global
logger = setup_logger()
