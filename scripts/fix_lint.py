#!/usr/bin/env python3
"""
Script pour corriger automatiquement les problèmes de lint du projet.
Usage: python scripts/fix_lint.py
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Exécute une commande et affiche le résultat."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode


def main():
    """Corrige tous les problèmes de lint."""
    project_root = Path(__file__).parent.parent

    print(f"📁 Projet : {project_root}")

    # 1. Formater avec Black
    returncode = run_command(
        f"cd {project_root} && .venv/bin/black ml_model/ tests/ examples/ --line-length 88",
        "Formatage avec Black",
    )

    # 2. Trier les imports avec isort
    returncode += run_command(
        f"cd {project_root} && .venv/bin/python -m isort ml_model/ tests/ examples/ --profile black",
        "Tri des imports avec isort",
    )

    # 3. Vérifier avec Flake8
    returncode += run_command(
        f"cd {project_root} && .venv/bin/python -m flake8 ml_model/ tests/ examples/ --max-line-length=88 --extend-ignore=E203,W503",
        "Vérification avec Flake8",
    )

    # 4. Lancer les tests
    returncode += run_command(
        f"cd {project_root} && .venv/bin/python -m pytest tests/test_basic.py -v",
        "Exécution des tests",
    )

    print(f"\n{'='*60}")
    if returncode == 0:
        print("✅ Tous les checks passent !")
    else:
        print("⚠️  Certains problèmes subsistent. Vérifiez les logs ci-dessus.")
    print(f"{'='*60}\n")

    return returncode


if __name__ == "__main__":
    sys.exit(main())
