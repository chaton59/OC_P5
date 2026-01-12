#!/usr/bin/env python3
"""
📦 Prédiction BATCH - Le plus simple possible

Usage: python demo_batch.py
"""

import os
import pandas as pd
import requests
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Pour utiliser l'API Hugging Face Spaces, changez l'URL ci-dessous
# API_URL = "https://asi-engineer-oc-p5.hf.space"
API_URL = "http://127.0.0.1:7860"  # API locale par défaut
API_KEY = None  # Pas besoin d'API key en mode DEBUG local

print("╔══════════════════════════════════════════════════════════╗")
print("║  📦 PRÉDICTION BATCH - Traitement CSV                    ║")
print("╚══════════════════════════════════════════════════════════╝\n")

# ═══════════════════════════════════════════════════════════════
# COLLECTE DES FICHIERS
# ═══════════════════════════════════════════════════════════════

# Obtenir le dossier du script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Chemins par défaut vers les fichiers d'exemple
default_sondage = os.path.join(script_dir, "02_predict_batch_sondage.csv")
default_eval = os.path.join(script_dir, "02_predict_batch_eval.csv")
default_sirh = os.path.join(script_dir, "02_predict_batch_sirh.csv")

print("📋 Voulez-vous utiliser les fichiers d'exemple du dossier ?")
print(f"   - {os.path.basename(default_sondage)}")
print(f"   - {os.path.basename(default_eval)}")
print(f"   - {os.path.basename(default_sirh)}")
use_defaults = input("\nUtiliser ces fichiers ? (O/n): ").strip().lower()

if use_defaults in ['', 'o', 'oui', 'y', 'yes']:
    sondage_path = default_sondage
    eval_path = default_eval
    sirh_path = default_sirh
    print("\n✅ Utilisation des fichiers d'exemple")
else:
    print("\nVeuillez fournir les 3 fichiers CSV:\n")
    sondage_path = input("📋 Chemin du fichier SONDAGE (.csv): ").strip()
    eval_path = input("📊 Chemin du fichier ÉVALUATION (.csv): ").strip()
    sirh_path = input("💼 Chemin du fichier SIRH (.csv): ").strip()

# Vérifier que les fichiers existent
for path in [sondage_path, eval_path, sirh_path]:
    if not os.path.exists(path):
        print(f"\n❌ ERREUR: Fichier introuvable: {path}")
        exit(1)

print(f"\n✅ Fichiers chargés:")
print(f"   - Sondage: {os.path.basename(sondage_path)}")
print(f"   - Évaluation: {os.path.basename(eval_path)}")
print(f"   - SIRH: {os.path.basename(sirh_path)}")

# ═══════════════════════════════════════════════════════════════
# ENVOI À L'API
# ═══════════════════════════════════════════════════════════════

print("\n⏳ Envoi des fichiers à l'API...")

files = {
    "sondage_file": open(sondage_path, "rb"),
    "eval_file": open(eval_path, "rb"),
    "sirh_file": open(sirh_path, "rb")
}

headers = {}
if API_KEY:
    headers["X-API-Key"] = API_KEY

try:
    response = requests.post(
        f"{API_URL}/predict/batch",
        files=files,
        headers=headers,
        timeout=120
    )
    response.raise_for_status()
    result = response.json()
    
    # ═══════════════════════════════════════════════════════════════
    # CRÉATION DU CSV DE SORTIE
    # ═══════════════════════════════════════════════════════════════
    
    print("\n✅ Prédictions reçues!")
    print(f"   Total employés traités: {result['total_employees']}")
    
    # Créer un DataFrame avec les résultats
    predictions_data = []
    for pred in result["predictions"]:
        predictions_data.append({
            "employee_id": pred["employee_id"],
            "prediction": "VA PARTIR" if pred["prediction"] == 1 else "VA RESTER",
            "prediction_code": pred["prediction"],
            "risk_level": pred["risk_level"],
            "probability_stay": f"{pred['probability_stay']:.2%}",
            "probability_leave": f"{pred['probability_leave']:.2%}"
        })
    
    df_results = pd.DataFrame(predictions_data)
    
    # Générer le nom du fichier de sortie
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"predictions_batch_{timestamp}.csv"
    
    # Sauvegarder dans le même dossier que ce script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_filename)
    
    # Sauvegarder dans le même dossier que ce script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_filename)
    
    df_results.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    # ═══════════════════════════════════════════════════════════════
    # AFFICHAGE DU RÉSUMÉ
    # ═══════════════════════════════════════════════════════════════
    
    print("\n" + "═"*60)
    print("                    📊 RÉSUMÉ")
    print("═"*60)
    
    summary = result["summary"]
    print(f"\n✅ Employés qui vont RESTER: {summary['total_stay']}")
    print(f"🏃 Employés qui vont PARTIR: {summary['total_leave']}")
    print(f"\n🔴 Risque ÉLEVÉ: {summary['high_risk_count']}")
    print(f"🟡 Risque MOYEN: {summary['medium_risk_count']}")
    print(f"🟢 Risque FAIBLE: {summary['low_risk_count']}")
    
    print("\n" + "═"*60)
    print(f"💾 Résultats sauvegardés dans:")
    print(f"   {output_path}")
    print("═"*60)
    
    # Afficher un échantillon
    print("\n📋 Aperçu des 5 premiers résultats:")
    print(df_results.head(5).to_string(index=False))
    
except requests.exceptions.RequestException as e:
    print(f"\n❌ ERREUR API: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Détails: {e.response.text}")
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
finally:
    # Fermer les fichiers
    for f in files.values():
        if not f.closed:
            f.close()
