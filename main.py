#!/usr/bin/env python3
"""
Pipeline principal d'entraînement du modèle Employee Turnover.

Ce script enchaîne:
1. Chargement et préprocessing des données
2. Entraînement du modèle XGBoost avec RandomizedSearchCV et SMOTE
3. Logging des résultats dans MLflow (params, metrics, artifacts, model)
4. Sauvegarde des encoders et scaler pour utilisation future

Usage:
    python main.py

Le modèle et les artifacts sont enregistrés dans MLflow pour:
- Suivi des expérimentations
- Reproductibilité
    Déploiement via Model Registry
"""
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
from ml_model.preprocess import preprocess_data
from ml_model.train_model import train_model


def main():
    """Pipeline principal d'entraînement."""
    print("=" * 80)
    print("🚀 PIPELINE D'ENTRAÎNEMENT - Employee Turnover Prediction")
    print("=" * 80)
    print()

    # Configuration MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("Employee_Turnover_Training")

    print("📊 Configuration MLflow:")
    print(f"   Tracking URI: {mlflow.get_tracking_uri()}")
    print("   Experiment: Employee_Turnover_Training")
    print()

    # Chemins des données
    data_paths = {
        "sondage_path": "data/extrait_sondage.csv",
        "eval_path": "data/extrait_eval.csv",
        "sirh_path": "data/extrait_sirh.csv",
    }

    # Vérifier que les fichiers existent
    for name, path in data_paths.items():
        if not Path(path).exists():
            raise FileNotFoundError(f"❌ Fichier manquant: {path}")

    print("✅ Fichiers de données trouvés")
    print()

    # ========================================================================
    # ÉTAPE 1 : Préprocessing
    # ========================================================================
    print("1️⃣  PRÉPROCESSING")
    print("-" * 80)

    X, y, scaler, onehot_encoder, ordinal_encoder = preprocess_data(data_paths)

    print(f"   Forme X: {X.shape}")
    print(f"   Forme y: {y.shape}")
    print(f"   Classes: {y.value_counts().to_dict()}")
    print(f"   Ratio déséquilibre: {(y == 0).sum() / (y == 1).sum():.2f}:1")
    print()

    # ========================================================================
    # ÉTAPE 2 : Entraînement avec MLflow tracking
    # ========================================================================
    print("2️⃣  ENTRAÎNEMENT")
    print("-" * 80)

    # Entraînement (déjà avec MLflow tracking dans train_model.py)
    model, best_params, cv_f1 = train_model(X, y)

    print("   ✅ Modèle entraîné")
    print(f"   🏆 Meilleur F1 CV: {cv_f1:.4f}")
    print()

    # Récupérer le run actif pour sauvegarder les artifacts
    active_run = mlflow.active_run()
    if active_run is None:
        # Si train_model a fermé le run, on en ouvre un nouveau
        active_run = mlflow.start_run()
        run_id = active_run.info.run_id
        should_end_run = True
    else:
        run_id = active_run.info.run_id
        should_end_run = False

    # Log des infos dataset
    mlflow.log_param("n_samples", len(X))
    mlflow.log_param("n_features", X.shape[1])
    mlflow.log_param("class_ratio", f"{(y == 0).sum()}:{(y == 1).sum()}")

    # ========================================================================
    # ÉTAPE 3 : Sauvegarde des artifacts (encoders, scaler)
    # ========================================================================
    print("3️⃣  SAUVEGARDE DES ARTIFACTS")
    print("-" * 80)

    # Créer dossier temporaire pour artifacts
    artifacts_dir = Path("artifacts_temp")
    artifacts_dir.mkdir(exist_ok=True)

    # Sauvegarder scaler
    scaler_path = artifacts_dir / "scaler.joblib"
    joblib.dump(scaler, scaler_path)
    mlflow.log_artifact(str(scaler_path), artifact_path="preprocessing")
    print("   ✅ Scaler sauvegardé")

    # Sauvegarder encoders (onehot et ordinal)
    onehot_path = artifacts_dir / "onehot_encoder.joblib"
    joblib.dump(onehot_encoder, onehot_path)
    mlflow.log_artifact(str(onehot_path), artifact_path="preprocessing")

    ordinal_path = artifacts_dir / "ordinal_encoder.joblib"
    joblib.dump(ordinal_encoder, ordinal_path)
    mlflow.log_artifact(str(ordinal_path), artifact_path="preprocessing")
    print("   ✅ Encoders sauvegardés (OneHot + Ordinal)")

    # Log git commit si disponible
    try:
        import subprocess

        git_commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .strip()
            .decode("utf-8")
        )
        mlflow.set_tag("git_commit", git_commit[:8])
        print(f"   ✅ Git commit: {git_commit[:8]}")
    except Exception:
        pass

    # Nettoyer artifacts temporaires
    scaler_path.unlink()
    onehot_path.unlink()
    ordinal_path.unlink()
    artifacts_dir.rmdir()

    print()

    # Fermer le run si on l'a ouvert
    if should_end_run:
        mlflow.end_run()

    # ========================================================================
    # RÉSUMÉ
    # ========================================================================
    print("=" * 80)
    print("✅ ENTRAÎNEMENT TERMINÉ")
    print("=" * 80)
    print()
    print(f"📊 Run ID: {run_id}")
    print(f"🎯 F1 Score (CV): {cv_f1:.4f}")
    print("📦 Artifacts sauvegardés dans MLflow")
    print()
    print("🌐 Pour visualiser les résultats:")
    print("   ./scripts/start_mlflow.sh")
    print("   ou: mlflow ui --backend-store-uri sqlite:///mlflow.db")
    print()
    print("📝 Pour charger le modèle:")
    print(f"   model = mlflow.sklearn.load_model('runs:/{run_id}/model')")
    print()


if __name__ == "__main__":
    main()
