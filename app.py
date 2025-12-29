#!/usr/bin/env python3
"""
App Gradio pour Hugging Face Spaces.

Lance l'interface Gradio pour la prédiction de turnover.
"""
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gradio_ui import launch_standalone

if __name__ == "__main__":
    launch_standalone()
