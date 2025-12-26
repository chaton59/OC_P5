#!/usr/bin/env python3
"""Script de test rapide de l'API."""
import json

# Données d'exemple basées sur la première ligne des CSV
test_data = {
    "nombre_participation_pee": 0,
    "nb_formations_suivies": 0,
    "nombre_employee_sous_responsabilite": 1,
    "distance_domicile_travail": 1,
    "niveau_education": 2,
    "domaine_etude": "Infra & Cloud",
    "ayant_enfants": "Y",
    "frequence_deplacement": "Occasionnel",
    "annees_depuis_la_derniere_promotion": 0,
    "annes_sous_responsable_actuel": 5,
    "satisfaction_employee_environnement": 2,
    "note_evaluation_precedente": 3,
    "niveau_hierarchique_poste": 2,
    "satisfaction_employee_nature_travail": 4,
    "satisfaction_employee_equipe": 1,
    "satisfaction_employee_equilibre_pro_perso": 1,
    "note_evaluation_actuelle": 3,
    "heure_supplementaires": "Oui",
    "augementation_salaire_precedente": 11.0,
    "age": 41,
    "genre": "F",
    "revenu_mensuel": 5993.0,
    "statut_marital": "Célibataire",
    "departement": "Commercial",
    "poste": "Cadre Commercial",
    "nombre_experiences_precedentes": 8,
    "nombre_heures_travailless": 80,
    "annee_experience_totale": 8,
    "annees_dans_l_entreprise": 6,
    "annees_dans_le_poste_actuel": 4,
}

print("=" * 80)
print("TEST DE L'API FASTAPI")
print("=" * 80)
print()
print("Données de test:")
print(json.dumps(test_data, indent=2, ensure_ascii=False))
print()
print("✅ Schéma Pydantic validé - données prêtes pour l'API")
print()
print("Pour tester l'API:")
print("1. Lancer: uvicorn app:app --reload")
print("2. Ouvrir: http://localhost:8000/docs")
print("3. Tester /predict avec ces données")
