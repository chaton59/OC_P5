#!/usr/bin/env python3
"""
📦 Prédiction BATCH via API Hugging Face (Gradio Client)

Usage: python demo_batch_hf.py
- Utilise par défaut les CSV d'exemple du dossier
- Envoie les 3 fichiers à la Space HF via Gradio Client
- Sauvegarde un CSV de résultats

Prérequis: pip install gradio_client
"""

import os
import sys
import pandas as pd
from datetime import datetime

try:
    from gradio_client import Client, handle_file
except ImportError:
    print("❌ gradio_client non installé. Installez-le avec:")
    print("   pip install gradio_client")
    sys.exit(1)

API_URL = os.getenv("HF_API_URL", "https://asi-engineer-oc-p5.hf.space")

print("╔══════════════════════════════════════════════════════════╗")
print("║  📦 Prédiction BATCH - API Hugging Face (Gradio)        ║")
print("╚══════════════════════════════════════════════════════════╝\n")
print(f"🌐 API: {API_URL}\n")

# Dossier du script
script_dir = os.path.dirname(os.path.abspath(__file__))
sondage_path = os.path.join(script_dir, "02_predict_batch_sondage.csv")
eval_path = os.path.join(script_dir, "02_predict_batch_eval.csv")
sirh_path = os.path.join(script_dir, "02_predict_batch_sirh.csv")

# Vérifier existence
for path in [sondage_path, eval_path, sirh_path]:
    if not os.path.exists(path):
        print(f"❌ Fichier introuvable: {path}")
        sys.exit(1)

print("✅ Fichiers d'exemple détectés:")
print(f"   - {os.path.basename(sondage_path)}")
print(f"   - {os.path.basename(eval_path)}")
print(f"   - {os.path.basename(sirh_path)}\n")

print("⏳ Connexion à l'API Gradio...")
try:
    client = Client(API_URL)
    print("✅ Connecté à l'API Gradio\n")
except Exception as e:
    print(f"❌ Impossible de se connecter: {e}")
    sys.exit(1)

print("⏳ Envoi des fichiers pour prédiction batch...")
try:
    result = client.predict(
        sondage_path=handle_file(sondage_path),
        eval_path=handle_file(eval_path),
        sirh_path=handle_file(sirh_path),
        api_name="/predict_batch",
    )
except Exception as e:
    print(f"❌ Erreur lors de la prédiction: {e}")
    sys.exit(1)

# Vérifier si erreur dans le résultat
if isinstance(result, dict) and "error" in result:
    print(f"\n❌ Erreur API: {result.get('error')}")
    print(f"   Message: {result.get('message')}")
    sys.exit(1)

# Construire le CSV de sortie
predictions_data = []
for pred in result.get("predictions", []):
    predictions_data.append(
        {
            "employee_id": pred.get("employee_id"),
            "prediction": "VA PARTIR" if pred.get("prediction") == 1 else "VA RESTER",
            "prediction_code": pred.get("prediction"),
            "risk_level": pred.get("risk_level"),
            "probability_stay": f"{pred.get('probability_stay', 0):.2%}",
            "probability_leave": f"{pred.get('probability_leave', 0):.2%}",
        }
    )

df = pd.DataFrame(predictions_data)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(script_dir, f"predictions_batch_hf_{timestamp}.csv")
df.to_csv(output_path, index=False, encoding="utf-8-sig")

# Affichage résumé
summary = result.get("summary", {})
total = result.get("total_employees", len(predictions_data))

print("\n" + "=" * 50)
print("📊 RÉSULTATS DE LA PRÉDICTION BATCH")
print("=" * 50)
print(f"\n👥 Total employés analysés: {total}")
print(f"✅ Vont rester:  {summary.get('total_stay', 'N/A')}")
print(f"❌ Vont partir:  {summary.get('total_leave', 'N/A')}")
print(f"\n🔴 Risque élevé:  {summary.get('high_risk_count', 'N/A')}")
print(f"🟠 Risque moyen:  {summary.get('medium_risk_count', 'N/A')}")
print(f"🟢 Risque faible: {summary.get('low_risk_count', 'N/A')}")

print(f"\n💾 Résultats sauvegardés: {os.path.basename(output_path)}")
print("\n✅ Prédiction batch terminée avec succès!")
