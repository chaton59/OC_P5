#!/usr/bin/env python3
"""
📦 Prédiction BATCH via API Hugging Face

Usage: python demo_batch_hf.py
- Utilise par défaut les CSV d'exemple du dossier
- Envoie les 3 fichiers à la Space HF
- Sauvegarde un CSV de résultats

Option: définir HF_API_URL pour surcharger l'URL par défaut.
"""

import os
import pandas as pd
import requests
from datetime import datetime

API_URL = os.getenv("HF_API_URL", "https://asi-engineer-oc-p5.hf.space")

print("╔══════════════════════════════════════════════════════════╗")
print("║  📦 Prédiction BATCH - API Hugging Face                 ║")
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
        raise SystemExit(1)

print("✅ Fichiers d'exemple détectés:")
print(f"   - {os.path.basename(sondage_path)}")
print(f"   - {os.path.basename(eval_path)}")
print(f"   - {os.path.basename(sirh_path)}\n")

print("⏳ Envoi des fichiers à l'API HF...")
files = {
    "sondage_file": open(sondage_path, "rb"),
    "eval_file": open(eval_path, "rb"),
    "sirh_file": open(sirh_path, "rb"),
}
headers = {}
api_key = os.getenv("HF_API_KEY")
if api_key:
    headers["X-API-Key"] = api_key

try:
    # 1) Tente FastAPI (si exposé)
    r = requests.post(f"{API_URL}/predict/batch", files=files, headers=headers, timeout=90)
    if r.status_code == 404:
        # 2) Fallback: endpoint Gradio API
        print("\nℹ️ Endpoint FastAPI indisponible, tentative via Gradio API (/api/predict_batch)...")
        r = requests.post(f"{API_URL}/api/predict_batch", files=files, headers=headers, timeout=90)
        if r.status_code == 404:
            print("\n❌ Endpoint HF introuvable (/predict/batch et /api/predict_batch).")
            print("   Vérifiez que la Space expose l'API FastAPI ou l'onglet Batch Gradio.")
            print("   Sinon, utilisez l'API locale (lancer_api.sh).")
            raise SystemExit(1)
    r.raise_for_status()
    result = r.json()

    # Construire le CSV de sortie
    predictions_data = []
    for pred in result.get("predictions", []):
        predictions_data.append({
            "employee_id": pred.get("employee_id"),
            "prediction": "VA PARTIR" if pred.get("prediction") == 1 else "VA RESTER",
            "prediction_code": pred.get("prediction"),
            "risk_level": pred.get("risk_level"),
            "probability_stay": f"{pred.get('probability_stay', 0):.2%}",
            "probability_leave": f"{pred.get('probability_leave', 0):.2%}",
        })

    df = pd.DataFrame(predictions_data)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(script_dir, f"predictions_batch_hf_{timestamp}.csv")
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    # Affichage
    summary = result.get("summary", {})
    print("\n" + "═"*60)
    print("                    📊 RÉSULTAT (HF)")
    print("═"*60)
    print(f"\n✅ Traités: {result.get('total_employees')} | RESTER: {summary.get('total_stay')} | PARTIR: {summary.get('total_leave')}")
    print(f"🔴 High: {summary.get('high_risk_count')}  🟡 Medium: {summary.get('medium_risk_count')}  🟢 Low: {summary.get('low_risk_count')}\n")
    print("📄 Aperçu:")
    print(df.head(5).to_string(index=False))
    print(f"\n💾 Sauvegardé: {output_path}")

finally:
    for f in files.values():
        try:
            f.close()
        except Exception:
            pass
