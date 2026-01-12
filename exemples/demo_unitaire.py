#!/usr/bin/env python3
"""
🔮 Prédiction UNITAIRE - Le plus simple possible

Usage: python demo_unitaire.py
"""

import requests

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Pour utiliser l'API Hugging Face Spaces, changez l'URL ci-dessous
# API_URL = "https://asi-engineer-oc-p5.hf.space"
API_URL = "http://127.0.0.1:7860"  # API locale par défaut
API_KEY = None  # Pas besoin d'API key en mode DEBUG local

print("╔══════════════════════════════════════════════════════════╗")
print("║  🔮 PRÉDICTION UNITAIRE - Risque de départ employé       ║")
print("╚══════════════════════════════════════════════════════════╝\n")

# ═══════════════════════════════════════════════════════════════
# COLLECTE DES DONNÉES
# ═══════════════════════════════════════════════════════════════

print("Veuillez renseigner les informations de l'employé:\n")

# === SONDAGE ===
print("📋 DONNÉES SONDAGE")
nombre_participation_pee = int(input("Nombre participations PEE (0-3): "))
nb_formations_suivies = int(input("Nombre formations suivies (0-6): "))
distance_domicile_travail = int(input("Distance domicile-travail en km (1-30): "))
niveau_education = int(input("Niveau d'éducation (1-5): "))
domaine_etude = input(
    "Domaine d'étude (Infra & Cloud, Transformation Digitale, Marketing, Entrepreunariat, Ressources Humaines, Autre): "
)
ayant_enfants = input("A des enfants? (Y/N): ").upper()
frequence_deplacement = input("Fréquence déplacement (Aucun, Occasionnel, Frequent): ")
annees_depuis_la_derniere_promotion = int(input("Années depuis dernière promotion: "))
annes_sous_responsable_actuel = int(input("Années sous responsable actuel (0-17): "))

# === ÉVALUATION ===
print("\n📊 DONNÉES ÉVALUATION")
satisfaction_employee_environnement = int(input("Satisfaction environnement (1-4): "))
note_evaluation_precedente = int(input("Note évaluation précédente (1-4): "))
niveau_hierarchique_poste = int(input("Niveau hiérarchique (1-5): "))
satisfaction_employee_nature_travail = int(input("Satisfaction nature travail (1-4): "))
satisfaction_employee_equipe = int(input("Satisfaction équipe (1-4): "))
satisfaction_employee_equilibre_pro_perso = int(
    input("Satisfaction équilibre pro/perso (1-4): ")
)
note_evaluation_actuelle = int(input("Note évaluation actuelle (3-4): "))
heure_supplementaires = input("Heures supplémentaires? (Oui/Non): ")
augementation_salaire_precedente = float(
    input("Augmentation salaire précédente en % (0-100): ")
)

# === SIRH ===
print("\n💼 DONNÉES RH")
age = int(input("Âge (18-60): "))
genre = input("Genre (M/F): ").upper()
revenu_mensuel = float(input("Revenu mensuel en € (1000-20000): "))
statut_marital = input("Statut marital (Célibataire, Marié(e), Divorcé(e)): ")
departement = input("Département (Commercial, Consulting, Ressources Humaines): ")
poste = input(
    "Poste (Cadre Commercial, Assistant de Direction, Consultant, Tech Lead, Manager, Senior Manager, Représentant Commercial, Directeur Technique, Ressources Humaines): "
)
nombre_experiences_precedentes = int(input("Nombre expériences précédentes (0-9): "))
annee_experience_totale = int(input("Années expérience totale: "))
annees_dans_l_entreprise = int(input("Années dans l'entreprise (0-40): "))
annees_dans_le_poste_actuel = int(input("Années dans le poste actuel (0-18): "))

# ═══════════════════════════════════════════════════════════════
# PRÉDICTION
# ═══════════════════════════════════════════════════════════════

employee_data = {
    "nombre_participation_pee": nombre_participation_pee,
    "nb_formations_suivies": nb_formations_suivies,
    "nombre_employee_sous_responsabilite": 1,
    "distance_domicile_travail": distance_domicile_travail,
    "niveau_education": niveau_education,
    "domaine_etude": domaine_etude,
    "ayant_enfants": ayant_enfants,
    "frequence_deplacement": frequence_deplacement,
    "annees_depuis_la_derniere_promotion": annees_depuis_la_derniere_promotion,
    "annes_sous_responsable_actuel": annes_sous_responsable_actuel,
    "satisfaction_employee_environnement": satisfaction_employee_environnement,
    "note_evaluation_precedente": note_evaluation_precedente,
    "niveau_hierarchique_poste": niveau_hierarchique_poste,
    "satisfaction_employee_nature_travail": satisfaction_employee_nature_travail,
    "satisfaction_employee_equipe": satisfaction_employee_equipe,
    "satisfaction_employee_equilibre_pro_perso": satisfaction_employee_equilibre_pro_perso,
    "note_evaluation_actuelle": note_evaluation_actuelle,
    "heure_supplementaires": heure_supplementaires,
    "augementation_salaire_precedente": augementation_salaire_precedente,
    "age": age,
    "genre": genre,
    "revenu_mensuel": revenu_mensuel,
    "statut_marital": statut_marital,
    "departement": departement,
    "poste": poste,
    "nombre_experiences_precedentes": nombre_experiences_precedentes,
    "nombre_heures_travailless": 80,
    "annee_experience_totale": annee_experience_totale,
    "annees_dans_l_entreprise": annees_dans_l_entreprise,
    "annees_dans_le_poste_actuel": annees_dans_le_poste_actuel,
}

print("\n⏳ Envoi de la requête à l'API...")

headers = {"Content-Type": "application/json"}
if API_KEY:
    headers["X-API-Key"] = API_KEY

try:
    response = requests.post(
        f"{API_URL}/predict", json=employee_data, headers=headers, timeout=30
    )
    response.raise_for_status()
    result = response.json()

    # ═══════════════════════════════════════════════════════════════
    # AFFICHAGE DU RÉSULTAT
    # ═══════════════════════════════════════════════════════════════

    print("\n" + "═" * 60)
    print("                    📊 RÉSULTAT")
    print("═" * 60)

    if result["prediction"] == 1:
        print("\n🏃 PRÉDICTION: L'EMPLOYÉ VA QUITTER L'ENTREPRISE")
    else:
        print("\n✅ PRÉDICTION: L'EMPLOYÉ VA RESTER")

    print(f"\n🎯 Niveau de risque: {result['risk_level']}")
    print(f"   Probabilité de rester: {result['probability_0']:.1%}")
    print(f"   Probabilité de partir: {result['probability_1']:.1%}")

    print("\n" + "═" * 60)

except requests.exceptions.RequestException as e:
    print(f"\n❌ ERREUR: {e}")
    if hasattr(e, "response") and e.response is not None:
        print(f"Détails: {e.response.text}")
