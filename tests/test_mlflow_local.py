#!/usr/bin/env python3
"""
Script de test local pour train_model.py avec MLflow.
Utilise preprocess_data pour charger et préparer les données.
"""
import os

import mlflow

from ml_model.preprocess import preprocess_data
from ml_model.train_model import train_model

# Configure MLflow pour utiliser SQLite (nécessaire pour Model Registry)
mlflow.set_tracking_uri("sqlite:///mlflow.db")

if __name__ == "__main__":
    print("🔄 Chargement et prétraitement des données...")
    # Chemins des fichiers de données
    data_paths = {
        "sondage_path": "data/extrait_sondage.csv",
        "eval_path": "data/extrait_eval.csv",
        "sirh_path": "data/extrait_sirh.csv",
    }

    X, y, scaler, onehot, ordinal = preprocess_data(raw_data_paths=data_paths)
    print(f"✅ Données prétraitées :")
    print(f"   X shape: {X.shape}, y shape: {y.shape}")
    print(f"   Distribution y: {y.value_counts().to_dict()}")

    print("\n🚀 Lancement de l'entraînement avec MLflow tracking...")
    print("   (Cela peut prendre quelques minutes avec n_iter=1000...)\n")

    best_model, best_params, cv_f1 = train_model(X, y)

    print(f"\n✅ Entraînement terminé !")
    print(f"   CV F1-score: {cv_f1:.4f}")

    print("\n📁 Vérification des artifacts MLflow dans ./mlruns :")
    if os.path.exists("./mlruns"):
        for root, dirs, files in os.walk("./mlruns"):
            level = root.replace("./mlruns", "").count(os.sep)
            indent = " " * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = " " * 2 * (level + 1)
            for file in files[:5]:  # Limite à 5 fichiers par dossier
                print(f"{subindent}{file}")
            if len(files) > 5:
                print(f"{subindent}... ({len(files) - 5} autres fichiers)")
    else:
        print("   ⚠️ Dossier ./mlruns non trouvé")

    print("\n💡 Pour visualiser les runs MLflow, exécutez :")
    print("   mlflow ui")
    print("   Puis ouvrez http://localhost:5000 dans votre navigateur")
