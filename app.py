#!/usr/bin/env python3
"""
App pour Hugging Face Spaces.

Lance FastAPI (port 8000) et Gradio (port 7860) simultanément.
"""
import sys
import os
import logging
import subprocess
import time
import signal
from threading import Thread

# Configurer le logging avant toute chose
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    force=True,
)
logger = logging.getLogger(__name__)

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.config import get_settings  # noqa: E402


# Variables globales pour les processus
fastapi_process = None
gradio_thread = None


def start_fastapi():
    """Lance le serveur FastAPI en subprocess."""
    global fastapi_process
    logger.info("🚀 Démarrage de FastAPI sur port 8000...")
    
    try:
        fastapi_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Logger la sortie de FastAPI
        for line in iter(fastapi_process.stdout.readline, ''):
            if line:
                logger.info(f"[FastAPI] {line.rstrip()}")
                
    except Exception as e:
        logger.error(f"❌ Erreur démarrage FastAPI: {e}", exc_info=True)


def start_gradio():
    """Lance l'interface Gradio."""
    logger.info("🎨 Démarrage de Gradio sur port 7860...")
    try:
        from src.gradio_ui import launch_standalone
        launch_standalone()
    except Exception as e:
        logger.error(f"❌ Erreur démarrage Gradio: {e}", exc_info=True)


def cleanup(signum=None, frame=None):
    """Nettoie les processus avant de quitter."""
    global fastapi_process
    
    logger.info("🛑 Arrêt des services...")
    
    if fastapi_process:
        logger.info("Arrêt de FastAPI...")
        fastapi_process.terminate()
        try:
            fastapi_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("FastAPI ne répond pas, forçage de l'arrêt...")
            fastapi_process.kill()
    
    logger.info("✅ Arrêt propre effectué")
    sys.exit(0)


if __name__ == "__main__":
    try:
        settings = get_settings()
        
        # Installer les handlers de signaux
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)
        
        logger.info("=" * 60)
        logger.info("🚀 Démarrage de l'application complète")
        logger.info("   - FastAPI sur http://0.0.0.0:8000")
        logger.info("   - Gradio sur http://0.0.0.0:7860")
        logger.info("=" * 60)
        
        # Lancer FastAPI en thread séparé
        fastapi_thread = Thread(target=start_fastapi, daemon=True)
        fastapi_thread.start()
        
        # Attendre que FastAPI démarre
        logger.info("⏳ Attente du démarrage de FastAPI...")
        time.sleep(5)
        
        # Vérifier que FastAPI est démarré
        import requests
        for i in range(10):
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    logger.info("✅ FastAPI démarré et opérationnel")
                    break
            except Exception:
                logger.info(f"⏳ Tentative {i+1}/10 de connexion à FastAPI...")
                time.sleep(2)
        else:
            logger.warning("⚠️ FastAPI ne répond pas, mais on continue...")
        
        # Lancer Gradio (bloquant - dans le thread principal)
        start_gradio()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Application arrêtée par l'utilisateur")
        cleanup()
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}", exc_info=True)
        cleanup()
        sys.exit(1)
