#!/usr/bin/env python3
"""
Exemple 2 : Comparer plusieurs modèles avec différents hyperparamètres
Usage: python examples/02_compare_models.py
"""
import mlflow
import pandas as pd
from mlflow.tracking import MlflowClient

# Configuration
mlflow.set_tracking_uri("sqlite:///mlflow.db")
client = MlflowClient()


def compare_all_runs(experiment_name="Default"):
    """Compare tous les runs d'une expérience."""

    print(f"📊 Comparaison de tous les runs dans '{experiment_name}'\n")

    # Récupérer l'expérience
    experiment = client.get_experiment_by_name(experiment_name)
    if not experiment:
        print(f"❌ Expérience '{experiment_name}' introuvable")
        return None

    # Récupérer tous les runs
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id], order_by=["start_time DESC"]
    )

    if not runs:
        print(f"❌ Aucun run trouvé")
        return None

    print(f"✅ {len(runs)} run(s) trouvé(s)\n")

    # Créer un DataFrame pour comparaison
    data = []
    for run in runs:
        from datetime import datetime

        row = {
            "run_id": run.info.run_id[:8],  # 8 premiers caractères
            "status": run.info.status,
            "start_time": datetime.fromtimestamp(run.info.start_time / 1000).strftime(
                "%Y-%m-%d %H:%M"
            ),
        }

        # Ajouter les métriques
        for metric_name in ["cv_f1", "test_precision", "test_recall", "test_f1"]:
            row[metric_name] = run.data.metrics.get(metric_name, None)

        # Ajouter quelques hyperparamètres importants
        for param_name in ["clf__n_estimators", "clf__max_depth", "clf__learning_rate"]:
            param_value = run.data.params.get(param_name, None)
            if param_value:
                try:
                    row[param_name] = (
                        float(param_value)
                        if "." in str(param_value)
                        else int(param_value)
                    )
                except:
                    row[param_name] = param_value

        data.append(row)

    # Créer DataFrame
    df = pd.DataFrame(data)

    # Afficher le tableau
    print("📈 Comparaison des modèles :")
    print("=" * 120)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 120)
    print(df.to_string(index=False))
    print("=" * 120)

    # Statistiques
    print(f"\n📊 Statistiques :")
    if "cv_f1" in df.columns:
        print(f"   CV F1 moyen     : {df['cv_f1'].mean():.4f}")
        print(f"   CV F1 max       : {df['cv_f1'].max():.4f}")
        print(f"   CV F1 min       : {df['cv_f1'].min():.4f}")
        print(f"   Écart-type      : {df['cv_f1'].std():.4f}")

    # Meilleur run
    if "cv_f1" in df.columns:
        best_idx = df["cv_f1"].idxmax()
        best_run = df.iloc[best_idx]
        print(f"\n🏆 Meilleur run : {best_run['run_id']}")
        print(f"   CV F1 : {best_run['cv_f1']:.4f}")

    return df


def plot_metrics_comparison(experiment_name="Default"):
    """Génère un graphique de comparaison (nécessite matplotlib)."""
    try:
        import matplotlib.pyplot as plt

        experiment = client.get_experiment_by_name(experiment_name)
        if not experiment:
            return

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id], order_by=["start_time ASC"]
        )

        # Extraire les données
        run_names = [f"Run {i+1}" for i in range(len(runs))]
        cv_f1_scores = [run.data.metrics.get("cv_f1", 0) for run in runs]
        test_f1_scores = [run.data.metrics.get("test_f1", 0) for run in runs]

        # Créer le graphique
        fig, ax = plt.subplots(figsize=(12, 6))

        x = range(len(runs))
        width = 0.35

        ax.bar(
            [i - width / 2 for i in x], cv_f1_scores, width, label="CV F1", alpha=0.8
        )
        ax.bar(
            [i + width / 2 for i in x],
            test_f1_scores,
            width,
            label="Test F1",
            alpha=0.8,
        )

        ax.set_xlabel("Runs")
        ax.set_ylabel("F1 Score")
        ax.set_title(f"Comparaison des F1 scores - Expérience: {experiment_name}")
        ax.set_xticks(x)
        ax.set_xticklabels(run_names, rotation=45)
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig("mlflow_comparison.png", dpi=300, bbox_inches="tight")
        print(f"\n📊 Graphique sauvegardé : mlflow_comparison.png")

    except ImportError:
        print("\n⚠️  matplotlib non installé, graphique non généré")
        print("   Installation : pip install matplotlib")


if __name__ == "__main__":
    # Comparer tous les runs
    df = compare_all_runs("Default")

    if df is not None:
        # Générer un graphique
        plot_metrics_comparison("Default")

        print(f"\n💡 Conseils :")
        print(f"   - Les runs avec CV F1 élevé sont de meilleurs candidats")
        print(
            f"   - Vérifier que test_f1 est cohérent avec cv_f1 (pas de surapprentissage)"
        )
        print(
            f"   - Favoriser les modèles avec moins de paramètres si performances similaires"
        )
