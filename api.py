#!/usr/bin/env python3
"""
API FastAPI pour le modèle Employee Turnover.

Cette API expose le modèle de prédiction de départ des employés avec :
- Validation stricte des inputs via Pydantic
- Preprocessing automatique
- Health check pour monitoring
- Documentation OpenAPI/Swagger automatique
- Interface Gradio optionnelle pour utilisation interactive
- Endpoint batch pour traitement de fichiers CSV
"""
import io
import time
from contextlib import asynccontextmanager
from typing import Any, Callable

import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.auth import verify_api_key
from src.config import get_settings
from src.logger import log_model_load, log_request, logger
from src.models import get_model_info, load_model
from src.preprocessing import (
    merge_csv_dataframes,
    preprocess_dataframe_for_prediction,
    preprocess_for_prediction,
)
from src.rate_limit import limiter
from src.schemas import (
    BatchPredictionOutput,
    EmployeeInput,
    EmployeePrediction,
    HealthCheck,
    PredictionOutput,
)

# Charger la configuration
settings = get_settings()
API_VERSION = settings.API_VERSION
GRADIO_ENABLED = settings.GRADIO_ENABLED


def conditional_rate_limit(
    limit: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Applique un rate limit seulement si DEBUG=False.

    En mode DEBUG (tests), pas de rate limiting pour éviter les échecs de tests.

    Args:
        limit: Limite à appliquer (ex: "20/minute")

    Returns:
        Décorateur de rate limiting ou fonction identité
    """
    if settings.DEBUG:
        # En mode DEBUG, retourner une fonction qui ne fait rien
        def no_limit(func):
            return func

        return no_limit
    else:
        # En production, appliquer le rate limit normal
        return limiter.limit(limit)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application.

    Charge le modèle au démarrage et le garde en cache.
    """
    logger.info(
        "🚀 Démarrage de l'API Employee Turnover...", extra={"version": API_VERSION}
    )

    start_time = time.time()
    try:
        # Pré-charger le modèle au démarrage
        model = load_model()
        duration_ms = (time.time() - start_time) * 1000

        model_type = type(model).__name__
        log_model_load(model_type, duration_ms, True)
        logger.info("✅ Modèle chargé avec succès")
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log_model_load("Unknown", duration_ms, False)
        logger.error("Le modèle n'a pas pu être chargé", extra={"error": str(e)})

    yield  # L'application tourne

    logger.info("🛑 Arrêt de l'API")


# Créer l'application FastAPI
app = FastAPI(
    title="Employee Turnover Prediction API",
    description="API de prédiction du turnover des employés avec XGBoost + SMOTE",
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Ajouter rate limiting
app.state.limiter = limiter


# Wrapper pour le handler de rate limit qui respecte l'interface FastAPI
def rate_limit_exception_handler(request: Request, exc: Exception) -> Response:
    """
    Handler pour les exceptions de rate limiting.

    Utilise le handler de slowapi mais avec l'interface FastAPI.
    """
    if isinstance(exc, RateLimitExceeded):
        return _rate_limit_exceeded_handler(request, exc)
    else:
        # Fallback pour autres exceptions
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )


app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)

# Configurer CORS (autoriser tous les domaines en dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware de logging des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware pour logger toutes les requêtes HTTP.
    """
    start_time = time.time()

    # Traiter la requête
    response = await call_next(request)

    # Calculer la durée
    duration_ms = (time.time() - start_time) * 1000

    # Logger
    log_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        client_host=request.client.host if request.client else None,
    )

    return response


@app.get("/health", response_model=HealthCheck, tags=["Monitoring"])
async def health_check():
    """
    Health check endpoint pour monitoring.

    Vérifie que l'API est opérationnelle et que le modèle est chargé.

    Returns:
        HealthCheck: Status de l'API et du modèle.

    Raises:
        HTTPException: 503 si le modèle n'est pas disponible.
    """
    try:
        model_info = get_model_info()

        return HealthCheck(
            status="healthy",
            model_loaded=model_info.get("cached", False),
            model_type=model_info.get("model_type", "Unknown"),
            version=API_VERSION,
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": "Model not available",
                "message": str(e),
            },
        )


@app.post(
    "/predict",
    response_model=PredictionOutput,
    tags=["Prediction"],
    dependencies=[Depends(verify_api_key)] if settings.is_api_key_required else [],
)
@conditional_rate_limit("20/minute")
async def predict(request: Request, employee: EmployeeInput):
    """
    Endpoint de prédiction du turnover d'un employé.

    **PROTÉGÉ PAR API KEY** : Requiert le header `X-API-Key` en production.

    Prend en entrée les données d'un employé, applique le preprocessing
    et retourne la prédiction avec les probabilités.

    Args:
        employee: Données de l'employé validées par Pydantic.

    Returns:
        PredictionOutput: Prédiction et probabilités.

    Raises:
        HTTPException: 401 si API key invalide ou manquante.
        HTTPException: 500 si erreur lors de la prédiction.

    Examples:
        ```bash
        # Avec authentification
        curl -X POST http://localhost:8000/predict \\
          -H "X-API-Key: your-secret-key" \\
          -H "Content-Type: application/json" \\
          -d '{...}'
        ```
    """
    try:
        # 1. Charger le modèle
        model = load_model()

        # 2. Préprocessing
        X = preprocess_for_prediction(employee)

        # 3. Prédiction
        prediction = int(model.predict(X)[0])

        # 4. Probabilités (si le modèle supporte predict_proba)
        try:
            probabilities = model.predict_proba(X)[0]
            prob_0 = float(probabilities[0])
            prob_1 = float(probabilities[1])
        except AttributeError:
            # Si le modèle ne supporte pas predict_proba
            prob_0 = 1.0 if prediction == 0 else 0.0
            prob_1 = 1.0 if prediction == 1 else 0.0

        # 5. Niveau de risque
        if prob_1 < 0.3:
            risk_level = "Low"
        elif prob_1 < 0.7:
            risk_level = "Medium"
        else:
            risk_level = "High"

        # 6. Enregistrer dans la base de données
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            from db_models import MLLog

            engine = create_engine(settings.DATABASE_URL)
            Session = sessionmaker(bind=engine)
            session = Session()

            log_entry = MLLog(
                input_json=employee.model_dump(),
                prediction="Oui" if prediction == 1 else "Non",
            )
            session.add(log_entry)
            session.commit()
            session.close()

            logger.info(f"Prediction logged to database: {prediction}")
        except Exception as db_error:
            logger.warning(f"Failed to log prediction to database: {db_error}")

        return PredictionOutput(
            prediction=prediction,
            probability_0=prob_0,
            probability_1=prob_1,
            risk_level=risk_level,
        )

    except Exception:
        logger.exception("Unexpected error during prediction")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Prediction failed",
                "message": "An unexpected error occurred. Please contact support.",
            },
        )


@app.post(
    "/predict/batch",
    response_model=BatchPredictionOutput,
    tags=["Prediction"],
    dependencies=[Depends(verify_api_key)] if settings.is_api_key_required else [],
)
@conditional_rate_limit("5/minute")
async def predict_batch(
    request: Request,
    sondage_file: UploadFile = File(..., description="Fichier CSV du sondage"),
    eval_file: UploadFile = File(..., description="Fichier CSV des évaluations"),
    sirh_file: UploadFile = File(..., description="Fichier CSV SIRH"),
):
    """
    Endpoint de prédiction batch à partir de fichiers CSV.

    **PROTÉGÉ PAR API KEY** : Requiert le header `X-API-Key` en production.

    Prend en entrée les 3 fichiers CSV (sondage, évaluation, SIRH),
    les fusionne, applique le preprocessing et retourne les prédictions
    pour tous les employés.

    Args:
        sondage_file: Fichier CSV contenant les données de sondage.
        eval_file: Fichier CSV contenant les données d'évaluation.
        sirh_file: Fichier CSV contenant les données SIRH.

    Returns:
        BatchPredictionOutput: Prédictions pour tous les employés.

    Raises:
        HTTPException: 400 si les fichiers sont invalides.
        HTTPException: 500 si erreur lors du traitement.
    """
    try:
        # 1. Lire les fichiers CSV
        sondage_content = await sondage_file.read()
        eval_content = await eval_file.read()
        sirh_content = await sirh_file.read()

        sondage_df = pd.read_csv(io.BytesIO(sondage_content))
        eval_df = pd.read_csv(io.BytesIO(eval_content))
        sirh_df = pd.read_csv(io.BytesIO(sirh_content))

        logger.info(
            f"Fichiers CSV chargés: sondage={len(sondage_df)}, "
            f"eval={len(eval_df)}, sirh={len(sirh_df)} lignes"
        )

        # 2. Fusionner les DataFrames
        merged_df = merge_csv_dataframes(sondage_df, eval_df, sirh_df)
        employee_ids = merged_df["original_employee_id"].tolist()
        merged_df = merged_df.drop(columns=["original_employee_id"])

        # Supprimer la colonne cible si présente
        if "a_quitte_l_entreprise" in merged_df.columns:
            merged_df = merged_df.drop(columns=["a_quitte_l_entreprise"])

        logger.info(f"DataFrame fusionné: {len(merged_df)} employés")

        # 3. Preprocessing
        X = preprocess_dataframe_for_prediction(merged_df)

        # 4. Charger le modèle et prédire
        model = load_model()
        predictions = model.predict(X.values)
        probabilities = model.predict_proba(X.values)

        # 5. Construire la réponse
        results = []
        risk_counts = {"Low": 0, "Medium": 0, "High": 0}
        leave_count = 0

        for i, emp_id in enumerate(employee_ids):
            prob_stay = float(probabilities[i][0])
            prob_leave = float(probabilities[i][1])
            pred = int(predictions[i])

            if prob_leave < 0.3:
                risk = "Low"
            elif prob_leave < 0.7:
                risk = "Medium"
            else:
                risk = "High"

            risk_counts[risk] += 1
            if pred == 1:
                leave_count += 1

            results.append(
                EmployeePrediction(
                    employee_id=int(emp_id),
                    prediction=pred,
                    probability_stay=prob_stay,
                    probability_leave=prob_leave,
                    risk_level=risk,
                )
            )

        summary = {
            "total_stay": len(results) - leave_count,
            "total_leave": leave_count,
            "high_risk_count": risk_counts["High"],
            "medium_risk_count": risk_counts["Medium"],
            "low_risk_count": risk_counts["Low"],
        }

        logger.info(f"Prédictions terminées: {summary}")

        return BatchPredictionOutput(
            total_employees=len(results),
            predictions=results,
            summary=summary,
        )

    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Empty CSV file",
                "message": "Un des fichiers CSV est vide.",
            },
        )
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Missing column",
                "message": f"Colonne manquante dans les CSV: {e}",
            },
        )
    except Exception as e:
        logger.exception("Unexpected error during batch prediction")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Batch prediction failed",
                "message": str(e),
            },
        )


if GRADIO_ENABLED:
    # Importer Gradio uniquement si l'UI est activée pour éviter une dépendance inutile en prod API-only
    import gradio as gr

    from src.gradio_ui import create_gradio_interface

    gradio_app = create_gradio_interface()
    app = gr.mount_gradio_app(app, gradio_app, path="/")
else:
    logger.info("Gradio UI désactivée (GRADIO_ENABLED=False)")


if __name__ == "__main__":
    import uvicorn

    print("\U0001f680 Lancement de l'API en mode d\u00e9veloppement...")
    print("\U0001f4d6 Documentation : http://localhost:8000/docs")
    print("\U0001f3a8 Interface Gradio : http://localhost:8000/")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
