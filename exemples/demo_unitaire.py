#!/usr/bin/env python3
"""
🔮 Prédiction UNITAIRE - Interface simple avec entrées numériques uniquement

Usage: python demo_unitaire.py
Note: Utilise l'API Gradio locale qui retourne du Markdown
"""

import re
import sys

try:
    from gradio_client import Client
except ImportError:
    print("❌ gradio_client non installé. Installez-le avec:")
    print("   pip install gradio_client")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
API_URL = "http://127.0.0.1:7860"  # API Gradio locale

# ═══════════════════════════════════════════════════════════════
# OPTIONS À AFFICHER (pour référence utilisateur)
# ═══════════════════════════════════════════════════════════════
DOMAINES = {
    1: "Infra & Cloud",
    2: "Transformation Digitale",
    3: "Marketing",
    4: "Entrepreunariat",
    5: "Ressources Humaines",
    6: "Autre",
}
FREQUENCES = {1: "Aucun", 2: "Occasionnel", 3: "Frequent"}
STATUTS = {1: "Célibataire", 2: "Marié(e)", 3: "Divorcé(e)"}
DEPARTEMENTS = {1: "Commercial", 2: "Consulting", 3: "Ressources Humaines"}
POSTES = {
    1: "Cadre Commercial",
    2: "Assistant de Direction",
    3: "Consultant",
    4: "Tech Lead",
    5: "Manager",
    6: "Senior Manager",
    7: "Représentant Commercial",
    8: "Directeur Technique",
    9: "Ressources Humaines",
}

print("╔══════════════════════════════════════════════════════════╗")
print("║  🔮 PRÉDICTION UNITAIRE - Risque de départ employé       ║")
print("║     (API locale - Entrées numériques uniquement)         ║")
print("╚══════════════════════════════════════════════════════════╝\n")

# ═══════════════════════════════════════════════════════════════
# COLLECTE DES DONNÉES - Tout en nombres !
# ═══════════════════════════════════════════════════════════════

print("═" * 60)
print("📋 DONNÉES SONDAGE")
print("═" * 60)
nombre_participation_pee = int(input("Participations PEE [0-3]: "))
nb_formations_suivies = int(input("Formations suivies [0-6]: "))
distance_domicile_travail = int(input("Distance domicile-travail km [1-30]: "))
niveau_education = int(
    input("Niveau éducation [1=Bac, 2=Bac+2, 3=Licence, 4=Master, 5=Doctorat]: ")
)

print(f"\nDomaine d'étude: {DOMAINES}")
domaine_choix = int(input("Choix [1-6]: "))
domaine_etude = DOMAINES.get(domaine_choix, "Autre")

ayant_enfants_choix = int(input("A des enfants? [0=Non, 1=Oui]: "))
ayant_enfants = "Y" if ayant_enfants_choix == 1 else "N"

print(f"\nFréquence déplacement: {FREQUENCES}")
freq_choix = int(input("Choix [1-3]: "))
frequence_deplacement = FREQUENCES.get(freq_choix, "Aucun")

annees_depuis_promo = int(input("Années depuis dernière promotion [0-15]: "))
annees_sous_responsable = int(input("Années sous responsable actuel [0-17]: "))

print("\n" + "═" * 60)
print("📊 DONNÉES ÉVALUATION")
print("═" * 60)
satisfaction_environnement = int(input("Satisfaction environnement [1-4]: "))
note_eval_precedente = int(input("Note évaluation précédente [1-4]: "))
niveau_hierarchique = int(input("Niveau hiérarchique [1-5]: "))
satisfaction_travail = int(input("Satisfaction nature travail [1-4]: "))
satisfaction_equipe = int(input("Satisfaction équipe [1-4]: "))
satisfaction_equilibre = int(input("Satisfaction équilibre pro/perso [1-4]: "))
note_eval_actuelle = int(input("Note évaluation actuelle [3-4]: "))
heures_sup_choix = int(input("Heures supplémentaires? [0=Non, 1=Oui]: "))
heure_supplementaires = "Oui" if heures_sup_choix == 1 else "Non"
augmentation_salaire = float(input("Augmentation salaire précédente % [0-25]: "))

print("\n" + "═" * 60)
print("💼 DONNÉES RH (SIRH)")
print("═" * 60)
age = int(input("Âge [18-60]: "))
genre_choix = int(input("Genre [1=Homme, 2=Femme]: "))
genre = "M" if genre_choix == 1 else "F"
revenu_mensuel = float(input("Revenu mensuel € [1000-20000]: "))

print(f"\nStatut marital: {STATUTS}")
statut_choix = int(input("Choix [1-3]: "))
statut_marital = STATUTS.get(statut_choix, "Célibataire")

print(f"\nDépartement: {DEPARTEMENTS}")
dept_choix = int(input("Choix [1-3]: "))
departement = DEPARTEMENTS.get(dept_choix, "Commercial")

print(f"\nPoste: {POSTES}")
poste_choix = int(input("Choix [1-9]: "))
poste = POSTES.get(poste_choix, "Consultant")

nombre_exp_precedentes = int(input("Expériences précédentes [0-9]: "))
annees_exp_totale = int(input("Années expérience totale [0-40]: "))
annees_entreprise = int(input("Années dans l'entreprise [0-40]: "))
annees_poste = int(input("Années dans le poste actuel [0-18]: "))

# ═══════════════════════════════════════════════════════════════
# PRÉDICTION VIA GRADIO CLIENT
# ═══════════════════════════════════════════════════════════════
print("\n⏳ Connexion à l'API Gradio locale...")

try:
    client = Client(API_URL)
    print("✅ Connecté\n")
    print("⏳ Envoi de la prédiction...")

    result = client.predict(
        nombre_participation_pee=nombre_participation_pee,
        nb_formations_suivies=nb_formations_suivies,
        nombre_employee_sous_responsabilite=1,
        distance_domicile_travail=distance_domicile_travail,
        niveau_education=niveau_education,
        domaine_etude=domaine_etude,
        ayant_enfants=ayant_enfants,
        frequence_deplacement=frequence_deplacement,
        annees_depuis_la_derniere_promotion=annees_depuis_promo,
        annes_sous_responsable_actuel=annees_sous_responsable,
        satisfaction_employee_environnement=satisfaction_environnement,
        note_evaluation_precedente=note_eval_precedente,
        niveau_hierarchique_poste=niveau_hierarchique,
        satisfaction_employee_nature_travail=satisfaction_travail,
        satisfaction_employee_equipe=satisfaction_equipe,
        satisfaction_employee_equilibre_pro_perso=satisfaction_equilibre,
        note_evaluation_actuelle=note_eval_actuelle,
        heure_supplementaires=heure_supplementaires,
        augementation_salaire_precedente=augmentation_salaire,
        age=age,
        genre=genre,
        revenu_mensuel=revenu_mensuel,
        statut_marital=statut_marital,
        departement=departement,
        poste=poste,
        nombre_experiences_precedentes=nombre_exp_precedentes,
        nombre_heures_travailless=80,
        annee_experience_totale=annees_exp_totale,
        annees_dans_l_entreprise=annees_entreprise,
        annees_dans_le_poste_actuel=annees_poste,
        api_name="/predict",
    )

    print("\n" + "═" * 60)
    print("📊 RÉSULTAT DE LA PRÉDICTION")
    print("═" * 60)

    # Le résultat est du Markdown - on l'affiche directement
    # mais on extrait aussi les valeurs clés
    if isinstance(result, str):
        # Extraire les probabilités du Markdown
        prob_depart = re.search(r"Probabilité de départ[^:]*:\s*([\d.]+)%", result)
        prob_maintien = re.search(r"Probabilité de maintien[^:]*:\s*([\d.]+)%", result)
        confiance = re.search(r"Confiance[^:]*:\s*([\d.]+)%", result)

        # Détecter le risque
        if "RISQUE ÉLEVÉ" in result:
            print("\n🔴 RISQUE ÉLEVÉ DE DÉPART")
        elif "RISQUE MOYEN" in result:
            print("\n🟠 RISQUE MOYEN DE DÉPART")
        else:
            print("\n🟢 RISQUE FAIBLE DE DÉPART")

        # Afficher les probabilités
        if prob_maintien:
            print(f"\n📈 Probabilité de rester:  {prob_maintien.group(1)}%")
        if prob_depart:
            print(f"📉 Probabilité de partir: {prob_depart.group(1)}%")
        if confiance:
            print(f"🎯 Confiance du modèle: {confiance.group(1)}%")

        # Afficher la prédiction
        if "Départ probable" in result:
            print("\n🚨 PRÉDICTION: VA PARTIR")
        else:
            print("\n✅ PRÉDICTION: VA RESTER")
    else:
        print(f"\n📋 Résultat: {result}")

except ConnectionError:
    print("\n❌ Impossible de se connecter à l'API Gradio locale.")
    print("   Lancez d'abord: python app.py")
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    sys.exit(1)
