#!/usr/bin/env python3
"""
App Gradio pour Hugging Face Spaces.

Lance l'interface Gradio pour la prédiction de turnover.
"""
import sys
import os
import logging

# Configurer le logging avant toute chose
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

if __name__ == "__main__":
    try:
        logger.info("🚀 Démarrage de l'application Gradio...")
        from src.gradio_ui import launch_standalone
        launch_standalone()
    except KeyboardInterrupt:
        logger.info("⏹️ Application arrêtée par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}", exc_info=True)
        sys.exit(1)
