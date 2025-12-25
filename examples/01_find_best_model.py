#!/usr/bin/env python3
"""
Exemple 1 : Trouver le meilleur modèle dans MLflow
Usage: python examples/01_find_best_model.py
"""
import mlflow
from mlflow.tracking import MlflowClient

# Configuration
mlflow.set_tracking_uri("sqlite:///mlflow.db")
client = MlflowClient()


def find_best_model(experiment_name="Default", metric="cv_f1"):
    """Trouve le meilleur modèle basé sur une métrique."""

    print(f"🔍 Recherche du meilleur modèle dans '{experiment_name}'...")
    print(f"📊 Métrique d'optimisation : {metric}\n")

    # Récupérer l'expérience
    experiment = client.get_experiment_by_name(experiment_name)
    if not experiment:
        print(f"❌ Expérience '{experiment_name}' introuvable")
        return None

    # Rechercher tous les runs
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="",  # Pas de filtre
        order_by=[f"metrics.{metric} DESC"],
        max_results=5,  # Top 5
    )

    if not runs:
        print(f"❌ Aucun run trouvé")
        return None

    print(f"📈 Top 5 des modèles :\n")
    print(f"{'Rank':<6} {'Run ID':<35} {metric:<12} {'Date':<20}")
    print("-" * 75)

    for i, run in enumerate(runs, 1):
        metric_value = run.data.metrics.get(metric, 0.0)
        timestamp = run.info.start_time
        from datetime import datetime

        date_str = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M")

        print(f"{i:<6} {run.info.run_id:<35} {metric_value:<12.4f} {date_str:<20}")

    # Meilleur modèle
    best_run = runs[0]
    best_metric = best_run.data.metrics.get(metric, 0.0)

    print(f"\n🏆 Meilleur modèle :")
    print(f"   Run ID    : {best_run.info.run_id}")
    print(f"   {metric:<10}: {best_metric:.4f}")
    print(f"   Status    : {best_run.info.status}")

    # Afficher les hyperparamètres
    print(f"\n⚙️  Hyperparamètres :")
    for key, value in best_run.data.params.items():
        print(f"   {key:<25} : {value}")

    # Afficher toutes les métriques
    print(f"\n📊 Métriques :")
    for key, value in best_run.data.metrics.items():
        print(f"   {key:<25} : {value:.4f}")

    return best_run.info.run_id


def load_best_model(run_id):
    """Charge le modèle à partir d'un run_id."""
    print(f"\n📦 Chargement du modèle...")

    model_uri = f"runs:/{run_id}/model"
    try:
        model = mlflow.sklearn.load_model(model_uri)
        print(f"✅ Modèle chargé avec succès")
        print(f"   Type : {type(model).__name__}")

        # Afficher la pipeline si c'est une Pipeline
        if hasattr(model, "steps"):
            print(f"   Pipeline steps :")
            for name, step in model.steps:
                print(f"      - {name}: {type(step).__name__}")

        return model
    except Exception as e:
        print(f"❌ Erreur lors du chargement : {e}")
        return None


if __name__ == "__main__":
    # Trouver le meilleur modèle
    best_run_id = find_best_model("Default", "cv_f1")

    if best_run_id:
        # Charger le modèle
        model = load_best_model(best_run_id)

        if model:
            print(f"\n💡 Pour utiliser ce modèle dans ton API :")
            print(f"   model_uri = 'runs:/{best_run_id}/model'")
            print(f"   model = mlflow.sklearn.load_model(model_uri)")
