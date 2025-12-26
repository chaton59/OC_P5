#!/usr/bin/env python3
"""
API FastAPI pour le modèle Employee Turnover.

Cette API expose le modèle de prédiction de départ des employés avec :
- Validation stricte des inputs via Pydantic
- Preprocessing automatique
- Health check pour monitoring
- Documentation OpenAPI/Swagger automatique
- Interface Gradio pour utilisation interactive
"""
import time
from contextlib import asynccontextmanager

import gradio as gr
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.auth import verify_api_key
from src.config import get_settings
from src.gradio_ui import create_gradio_interface
from src.logger import logger, log_model_load, log_request
from src.models import get_model_info, load_model
from src.preprocessing import preprocess_for_prediction
from src.rate_limit import limiter
from src.schemas import EmployeeInput, HealthCheck, PredictionOutput

# Charger la configuration
settings = get_settings()
API_VERSION = settings.API_VERSION


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
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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


@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint racine avec informations sur l'API.
    """
    return {
        "message": "Employee Turnover Prediction API",
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/health",
        "predict": "/predict (POST)",
    }


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
@limiter.limit("20/minute")
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


# Monter l'interface Gradio sur /ui
gradio_app = create_gradio_interface()
app = gr.mount_gradio_app(app, gradio_app, path="/ui")


if __name__ == "__main__":
    import uvicorn

    print("🚀 Lancement de l'API en mode développement...")
    print("📖 Documentation : http://localhost:8000/docs")
    print("🎨 Interface Gradio : http://localhost:8000/ui")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
