"""Configuration pytest pour ajouter le dossier racine au PYTHONPATH."""
import sys
from pathlib import Path

# Ajouter le dossier racine du projet au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
