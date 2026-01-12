#!/usr/bin/env python3
"""
📦 Prédiction BATCH - API Hugging Face (Gradio)

Usage: python demo_batch_hf.py
Prérequis: pip install gradio_client pandas
"""

import os
import sys
from datetime import datetime

try:
    import pandas as pd
    from gradio_client import Client, handle_file
except ImportError:
    print("❌ Dépendances manquantes. Installez avec:")
    print("   pip install gradio_client pandas")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
API_URL = os.getenv("HF_API_URL", "https://asi-engineer-oc-p5.hf.space")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Fichiers par défaut
DEFAULT_FILES = {
    "eval": os.path.join(SCRIPT_DIR, "02_predict_batch_eval.csv"),
    "sirh": os.path.join(SCRIPT_DIR, "02_predict_batch_sirh.csv"),
    "sondage": os.path.join(SCRIPT_DIR, "02_predict_batch_sondage.csv"),
}

print("╔══════════════════════════════════════════════════════════╗")
print("║  📦 PRÉDICTION BATCH - API Hugging Face                  ║")
print("╚══════════════════════════════════════════════════════════╝")
print(f"\n🌐 API: {API_URL}\n")

# ═══════════════════════════════════════════════════════════════
# SÉLECTION DES FICHIERS
# ═══════════════════════════════════════════════════════════════
print("═" * 60)
print("📁 SÉLECTION DES FICHIERS CSV")
print("═" * 60)

use_default = (
    input("\nUtiliser les fichiers exemples par défaut? [O/n]: ").strip().lower()
)

if use_default in ("", "o", "oui", "y", "yes"):
    fichier_eval = DEFAULT_FILES["eval"]
    fichier_sirh = DEFAULT_FILES["sirh"]
    fichier_sondage = DEFAULT_FILES["sondage"]
    print(f"\n📄 Évaluation: {os.path.basename(fichier_eval)}")
    print(f"📄 SIRH:       {os.path.basename(fichier_sirh)}")
    print(f"📄 Sondage:    {os.path.basename(fichier_sondage)}")
else:
    print("\nEntrez les chemins des fichiers CSV:")
    fichier_eval = input("📄 Fichier évaluation: ").strip()
    fichier_sirh = input("📄 Fichier SIRH: ").strip()
    fichier_sondage = input("📄 Fichier sondage: ").strip()

# Vérification des fichiers
for name, path in [
    ("Évaluation", fichier_eval),
    ("SIRH", fichier_sirh),
    ("Sondage", fichier_sondage),
]:
    if not os.path.exists(path):
        print(f"\n❌ Fichier {name} introuvable: {path}")
        sys.exit(1)

# ═══════════════════════════════════════════════════════════════
# PRÉDICTION BATCH
# ═══════════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("⏳ TRAITEMENT EN COURS...")
print("═" * 60)

try:
    print("\n⏳ Connexion à l'API...")
    client = Client(API_URL)
    print("✅ Connecté")

    print("⏳ Envoi des fichiers...")
    result = client.predict(
        fichier_eval=handle_file(fichier_eval),
        fichier_sirh=handle_file(fichier_sirh),
        fichier_sondage=handle_file(fichier_sondage),
        api_name="/predict_batch",
    )

    # ═══════════════════════════════════════════════════════════════
    # AFFICHAGE DU RÉSULTAT
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "═" * 60)
    print("📊 RÉSULTAT DE LA PRÉDICTION BATCH")
    print("═" * 60)

    if isinstance(result, dict):
        # Lecture du fichier résultat
        result_path = result.get("value") or result.get("path")
        if result_path and os.path.exists(result_path):
            df = pd.read_csv(result_path)
            total = len(df)

            # Statistiques
            if "prediction" in df.columns:
                restent = (df["prediction"] == "Reste").sum()
                partent = (df["prediction"] == "Part").sum()
            else:
                restent = partent = 0

            if "risk_level" in df.columns:
                risque_eleve = (df["risk_level"] == "Élevé").sum()
                risque_moyen = (df["risk_level"] == "Moyen").sum()
                risque_faible = (df["risk_level"] == "Faible").sum()
            else:
                risque_eleve = risque_moyen = risque_faible = 0

            # Affichage des stats
            print(f"\n👥 Total employés analysés: {total}")
            print(f"\n📈 Vont RESTER:  {restent} ({100 * restent / total:.1f}%)")
            print(f"📉 Vont PARTIR:  {partent} ({100 * partent / total:.1f}%)")

            print(f"\n🟢 Risque faible: {risque_faible}")
            print(f"🟠 Risque moyen:  {risque_moyen}")
            print(f"🔴 Risque élevé:  {risque_eleve}")

            # Sauvegarde
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(SCRIPT_DIR, f"predictions_batch_{timestamp}.csv")
            df.to_csv(output_file, index=False)

            print("\n" + "─" * 60)
            print(f"💾 Fichier sauvegardé: {os.path.basename(output_file)}")
            print("─" * 60)

            # Aperçu
            print("\n📋 Aperçu des résultats:")
            cols = ["employee_id", "prediction", "prob_depart", "risk_level"]
            cols_exist = [c for c in cols if c in df.columns]
            if cols_exist:
                print(df[cols_exist].head(10).to_string(index=False))
        else:
            print(f"\n⚠️ Fichier résultat non trouvé: {result_path}")
    else:
        print(f"\n📋 Résultat: {result}")

    print("\n✅ Prédiction batch terminée avec succès!")

except Exception as e:
    print(f"\n❌ Erreur: {e}")
    sys.exit(1)
