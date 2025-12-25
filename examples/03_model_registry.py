#!/usr/bin/env python3
"""
Exemple 3 : Gérer le Model Registry (versions, stages, promotion)
Usage: python examples/03_model_registry.py
"""
import mlflow
from mlflow.tracking import MlflowClient

# Configuration
mlflow.set_tracking_uri("sqlite:///mlflow.db")
client = MlflowClient()


def list_registered_models():
    """Liste tous les modèles enregistrés dans le Registry."""

    print("📦 Modèles enregistrés dans le Model Registry :\n")

    models = client.search_registered_models()

    if not models:
        print("❌ Aucun modèle enregistré")
        return []

    for rm in models:
        print(f"🔹 {rm.name}")
        print(f"   Description : {rm.description or 'N/A'}")
        print(f"   Création    : {rm.creation_timestamp}")
        print(f"   Versions    : {len(rm.latest_versions)}")

        # Lister les versions
        versions = client.search_model_versions(f"name='{rm.name}'")
        for mv in versions:
            stage = mv.current_stage
            emoji = (
                "🚀" if stage == "Production" else "🧪" if stage == "Staging" else "📝"
            )
            print(f"      {emoji} Version {mv.version} - {stage}")
            print(f"         Run ID: {mv.run_id}")
            print(f"         Source: {mv.source}")
        print()

    return models


def get_model_details(model_name="XGBoost_Employee_Turnover"):
    """Affiche les détails d'un modèle spécifique."""

    print(f"🔍 Détails du modèle '{model_name}' :\n")

    try:
        # Récupérer les infos du modèle
        rm = client.get_registered_model(model_name)

        from datetime import datetime

        print(f"📦 Informations générales :")
        print(f"   Nom         : {rm.name}")
        print(f"   Description : {rm.description or 'N/A'}")
        print(
            f"   Création    : {datetime.fromtimestamp(rm.creation_timestamp / 1000).strftime('%Y-%m-%d %H:%M')}"
        )
        print(
            f"   Dernière MAJ: {datetime.fromtimestamp(rm.last_updated_timestamp / 1000).strftime('%Y-%m-%d %H:%M')}"
        )

        # Lister toutes les versions
        versions = client.search_model_versions(f"name='{model_name}'")

        print(f"\n📊 Versions ({len(versions)}) :")
        print(f"{'Version':<10} {'Stage':<15} {'Run ID':<35} {'Date':<20}")
        print("-" * 85)

        for mv in sorted(versions, key=lambda v: int(v.version), reverse=True):
            date_str = datetime.fromtimestamp(mv.creation_timestamp / 1000).strftime(
                "%Y-%m-%d %H:%M"
            )
            print(
                f"{mv.version:<10} {mv.current_stage:<15} {mv.run_id:<35} {date_str:<20}"
            )

        # Afficher la version en production
        prod_versions = [v for v in versions if v.current_stage == "Production"]
        if prod_versions:
            print(f"\n🚀 Version en production : {prod_versions[0].version}")
        else:
            print(f"\n⚠️  Aucune version en production")

        return rm

    except Exception as e:
        print(f"❌ Erreur : {e}")
        return None


def promote_model(model_name, version, stage="Staging"):
    """
    Promouvoir une version de modèle vers un stage.

    Args:
        model_name: Nom du modèle
        version: Numéro de version
        stage: "Staging", "Production", ou "Archived"
    """

    print(f"🔄 Promotion du modèle '{model_name}' v{version} → {stage}...")

    try:
        # Transition vers le nouveau stage
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage,
            archive_existing_versions=True,  # Archive les anciennes versions du même stage
        )

        print(f"✅ Modèle promu avec succès !")
        print(f"   {model_name} v{version} est maintenant en {stage}")

        # Afficher l'état mis à jour
        mv = client.get_model_version(model_name, version)
        print(f"   Status : {mv.status}")

    except Exception as e:
        print(f"❌ Erreur lors de la promotion : {e}")


def load_model_from_registry(
    model_name="XGBoost_Employee_Turnover", stage="Production"
):
    """Charge un modèle depuis le Registry."""

    print(f"📦 Chargement du modèle '{model_name}' ({stage})...\n")

    model_uri = f"models:/{model_name}/{stage}"

    try:
        model = mlflow.sklearn.load_model(model_uri)
        print(f"✅ Modèle chargé avec succès")
        print(f"   URI  : {model_uri}")
        print(f"   Type : {type(model).__name__}")

        return model

    except mlflow.exceptions.MlflowException as e:
        print(f"⚠️  Aucun modèle en {stage}")
        print(f"   Essai avec 'latest'...")

        # Fallback sur latest
        model_uri = f"models:/{model_name}/latest"
        model = mlflow.sklearn.load_model(model_uri)
        print(f"✅ Dernière version chargée")

        return model


def demo_workflow():
    """Démo du workflow complet de gestion des modèles."""

    print("=" * 80)
    print("🎯 DEMO - Workflow Model Registry")
    print("=" * 80 + "\n")

    # 1. Lister les modèles
    print("1️⃣  Liste des modèles\n")
    models = list_registered_models()

    if not models:
        print("⚠️  Aucun modèle trouvé. Exécute d'abord un training avec MLflow.")
        return

    # 2. Détails du premier modèle
    model_name = models[0].name
    print("\n" + "=" * 80)
    print(f"2️⃣  Détails du modèle '{model_name}'\n")
    get_model_details(model_name)

    # 3. Exemple de promotion (commenté pour ne pas modifier l'état)
    print("\n" + "=" * 80)
    print("3️⃣  Promotion d'un modèle\n")
    print("💡 Pour promouvoir la version 1 en Production :")
    print(f"   promote_model('{model_name}', version=1, stage='Production')")
    print("   (Décommente dans le code pour exécuter)")

    # Décommente cette ligne pour promouvoir réellement :
    # promote_model(model_name, version=1, stage="Production")

    # 4. Charger un modèle
    print("\n" + "=" * 80)
    print("4️⃣  Chargement d'un modèle\n")

    # Essayer de charger depuis Production
    try:
        model = load_model_from_registry(model_name, "Production")
    except:
        print("⚠️  Aucun modèle en Production, chargement de 'latest'")
        model = load_model_from_registry(model_name, "None")

    print("\n" + "=" * 80)
    print("✅ Demo terminée !")
    print("=" * 80)


if __name__ == "__main__":
    demo_workflow()
