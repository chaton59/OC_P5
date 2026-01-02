#!/usr/bin/env python3
"""
Script de démonstration complet de l'API Employee Turnover Prediction.

Ce script montre toutes les fonctionnalités de l'API déployée sur HuggingFace Spaces :
- Health check
- Prédiction unitaire (POST /predict)
- Prédiction batch avec fichiers CSV (POST /predict/batch)
- Gestion des erreurs de validation

Usage:
    # Avec API Key (mode production)
    API_KEY=votre-cle python tests/test_api_demo.py

    # Sans API Key (mode DEBUG sur HF)
    python tests/test_api_demo.py

L'API est hébergée sur: https://asi-engineer-oc-p5-dev.hf.space
"""
import json
import os
import sys
from pathlib import Path

import pytest
import requests

# Configuration de l'API
API_BASE_URL = os.getenv("API_URL", "https://asi-engineer-oc-p5-dev.hf.space")
# API Key par défaut (celle configurée dans le Dockerfile HuggingFace)
API_KEY = os.getenv("API_KEY", "change-me-in-production")

# Headers avec API Key
HEADERS = {"Content-Type": "application/json", "X-API-Key": API_KEY}
print(f"🔑 API Key configurée: {API_KEY[:10]}...")

# Chemin vers les fichiers CSV de données
DATA_DIR = Path(__file__).parent.parent / "data"
SONDAGE_FILE = DATA_DIR / "extrait_sondage.csv"
EVAL_FILE = DATA_DIR / "extrait_eval.csv"
SIRH_FILE = DATA_DIR / "extrait_sirh.csv"


def print_section(title: str) -> None:
    """Affiche un titre de section."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def can_reach_api():
    """Vérifie si l'API est accessible."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return "status" in data and data["status"] == "healthy"
        return False
    except Exception:
        return False


@pytest.mark.skipif(
    not can_reach_api(),
    reason="API non accessible (tests d'intégration pour l'API déployée)",
)
def test_root_endpoint():
    """Test de l'endpoint racine (GET /) - Interface Gradio."""
    print_section("1. TEST INTERFACE GRADIO (GET /)")

    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=30)
        print(f"Status: {response.status_code}")

        # L'endpoint racine retourne l'interface Gradio (HTML, pas JSON)
        if response.status_code == 200:
            if (
                "gradio" in response.text.lower()
                or "<!doctype html>" in response.text.lower()
            ):
                print("✅ Interface Gradio accessible")
                assert True
            else:
                print("⚠️ Réponse inattendue (pas Gradio)")
                assert False
        else:
            assert False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        assert False


@pytest.mark.skipif(
    not can_reach_api(),
    reason="API non accessible (tests d'intégration pour l'API déployée)",
)
@pytest.mark.skipif(
    not can_reach_api(),
    reason="API non accessible (tests d'intégration pour l'API déployée)",
)
def test_health_endpoint():
    """Test de l'endpoint de santé (GET /health)."""
    print_section("2. TEST HEALTH CHECK (GET /health)")

    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=30)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")

        # Vérifications
        assert data["status"] == "healthy", "Status devrait être 'healthy'"
        assert data["model_loaded"] is True, "Modèle devrait être chargé"
        print("\n✅ Health check OK - Modèle chargé et prêt")
        assert True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        assert False


@pytest.mark.skipif(
    not can_reach_api(),
    reason="API non accessible (tests d'intégration pour l'API déployée)",
)
def test_predict_single():
    """Test de prédiction unitaire (POST /predict)."""
    print_section("3. TEST PRÉDICTION UNITAIRE (POST /predict)")

    # Données d'un employé type (valeurs dans les contraintes)
    employee_data = {
        # SONDAGE
        "nombre_participation_pee": 1,
        "nb_formations_suivies": 3,
        "nombre_employee_sous_responsabilite": 1,  # Fixe
        "distance_domicile_travail": 10,
        "niveau_education": 3,
        "domaine_etude": "Infra & Cloud",
        "ayant_enfants": "Y",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 2,
        "annes_sous_responsable_actuel": 5,
        # EVALUATION
        "satisfaction_employee_environnement": 3,
        "note_evaluation_precedente": 3,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Non",
        "augementation_salaire_precedente": 5.0,
        # SIRH
        "age": 35,
        "genre": "M",
        "revenu_mensuel": 5000.0,
        "statut_marital": "Marié(e)",
        "departement": "Commercial",
        "poste": "Consultant",
        "nombre_experiences_precedentes": 3,
        "nombre_heures_travailless": 80,  # Fixe
        "annee_experience_totale": 10,
        "annees_dans_l_entreprise": 5,
        "annees_dans_le_poste_actuel": 3,
    }

    try:
        print("📤 Envoi des données employé...")
        print(
            f"Données: {json.dumps(employee_data, indent=2, ensure_ascii=False)[:500]}..."
        )

        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=employee_data,
            headers=HEADERS,
            timeout=60,
        )

        print("\n📥 Réponse:")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")

            # Affichage lisible
            prediction = (
                "Départ probable" if data["prediction"] == 1 else "Maintien probable"
            )
            risk_emoji = {"Low": "🟢", "Medium": "🟠", "High": "🔴"}.get(
                data["risk_level"], "⚪"
            )

            print("\n📊 RÉSULTAT:")
            print(f"   {risk_emoji} Risque: {data['risk_level']}")
            print(f"   📈 Prédiction: {prediction}")
            print(f"   🎯 Probabilité de départ: {data['probability_1']:.1%}")
            print(f"   ✅ Probabilité de maintien: {data['probability_0']:.1%}")
            assert True
        else:
            print(f"Response: {response.text}")
            assert False

    except Exception as e:
        print(f"❌ Erreur: {e}")
        assert False


@pytest.mark.skipif(
    not can_reach_api(),
    reason="API non accessible (tests d'intégration pour l'API déployée)",
)
def test_predict_high_risk():
    """Test avec un employé à haut risque de départ."""
    print_section("4. TEST EMPLOYÉ À HAUT RISQUE")

    # Profil à risque : faible satisfaction, pas de promotion, heures sup
    high_risk_employee = {
        "nombre_participation_pee": 0,
        "nb_formations_suivies": 0,
        "nombre_employee_sous_responsabilite": 1,
        "distance_domicile_travail": 25,
        "niveau_education": 2,
        "domaine_etude": "Autre",
        "ayant_enfants": "N",
        "frequence_deplacement": "Frequent",
        "annees_depuis_la_derniere_promotion": 10,
        "annes_sous_responsable_actuel": 8,
        "satisfaction_employee_environnement": 1,
        "note_evaluation_precedente": 2,
        "niveau_hierarchique_poste": 1,
        "satisfaction_employee_nature_travail": 1,
        "satisfaction_employee_equipe": 1,
        "satisfaction_employee_equilibre_pro_perso": 1,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Oui",
        "augementation_salaire_precedente": 0.0,
        "age": 28,
        "genre": "F",
        "revenu_mensuel": 2000.0,
        "statut_marital": "Célibataire",
        "departement": "Commercial",
        "poste": "Représentant Commercial",
        "nombre_experiences_precedentes": 1,
        "nombre_heures_travailless": 80,
        "annee_experience_totale": 3,
        "annees_dans_l_entreprise": 2,
        "annees_dans_le_poste_actuel": 2,
    }

    try:
        print(
            "📤 Envoi profil à risque (faible satisfaction, heures sup, pas de promo)..."
        )

        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=high_risk_employee,
            headers=HEADERS,
            timeout=60,
        )

        if response.status_code == 200:
            data = response.json()
            risk_emoji = {"Low": "🟢", "Medium": "🟠", "High": "🔴"}.get(
                data["risk_level"], "⚪"
            )

            print("\n📊 RÉSULTAT EMPLOYÉ À RISQUE:")
            print(f"   {risk_emoji} Risque: {data['risk_level']}")
            print(f"   🎯 Probabilité de départ: {data['probability_1']:.1%}")

            if data["risk_level"] == "High" or data["probability_1"] > 0.5:
                print("\n   ⚠️  Comme attendu, cet employé présente un risque élevé !")
            assert True
        else:
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            assert False

    except Exception as e:
        print(f"❌ Erreur: {e}")
        assert False


@pytest.mark.skipif(
    not can_reach_api(),
    reason="API non accessible (tests d'intégration pour l'API déployée)",
)
def test_predict_batch():
    """Test de prédiction batch avec les 3 fichiers CSV."""
    print_section("5. TEST PRÉDICTION BATCH (POST /predict/batch)")

    # Vérifier que les fichiers existent
    for f in [SONDAGE_FILE, EVAL_FILE, SIRH_FILE]:
        if not f.exists():
            print(f"❌ Fichier manquant: {f}")
            assert False

    try:
        print("📂 Fichiers CSV utilisés:")
        print(f"   - Sondage: {SONDAGE_FILE}")
        print(f"   - Évaluation: {EVAL_FILE}")
        print(f"   - SIRH: {SIRH_FILE}")

        # Ouvrir les fichiers
        files = {
            "sondage_file": (
                "extrait_sondage.csv",
                open(SONDAGE_FILE, "rb"),
                "text/csv",
            ),
            "eval_file": ("extrait_eval.csv", open(EVAL_FILE, "rb"), "text/csv"),
            "sirh_file": ("extrait_sirh.csv", open(SIRH_FILE, "rb"), "text/csv"),
        }

        print("\n📤 Envoi des 3 fichiers CSV à l'API...")
        # Pour les uploads de fichiers, on utilise seulement X-API-Key (pas Content-Type)
        file_headers = {"X-API-Key": API_KEY} if API_KEY else {}
        response = requests.post(
            f"{API_BASE_URL}/predict/batch",
            files=files,
            headers=file_headers,
            timeout=120,
        )

        # Fermer les fichiers
        for _, file_tuple in files.items():
            file_tuple[1].close()

        print("\n📥 Réponse:")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Afficher le résumé
            print("\n📊 RÉSUMÉ DES PRÉDICTIONS:")
            print(f"   Total employés analysés: {data['total_employees']}")
            print(f"   🟢 Risque faible: {data['summary']['low_risk_count']}")
            print(f"   🟠 Risque moyen: {data['summary']['medium_risk_count']}")
            print(f"   🔴 Risque élevé: {data['summary']['high_risk_count']}")
            print(f"   ➡️  Prédiction maintien: {data['summary']['total_stay']}")
            print(f"   ⬅️  Prédiction départ: {data['summary']['total_leave']}")

            # Afficher les 5 premiers employés à haut risque
            high_risk = [p for p in data["predictions"] if p["risk_level"] == "High"]
            if high_risk:
                print("\n🔴 TOP 5 EMPLOYÉS À HAUT RISQUE:")
                for emp in sorted(
                    high_risk, key=lambda x: x["probability_leave"], reverse=True
                )[:5]:
                    print(
                        f"   ID {emp['employee_id']:4d}: {emp['probability_leave']:.1%} de départ"
                    )

            # Afficher les 5 employés les plus stables
            low_risk = [p for p in data["predictions"] if p["risk_level"] == "Low"]
            if low_risk:
                print("\n🟢 TOP 5 EMPLOYÉS LES PLUS STABLES:")
                for emp in sorted(
                    low_risk, key=lambda x: x["probability_stay"], reverse=True
                )[:5]:
                    print(
                        f"   ID {emp['employee_id']:4d}: {emp['probability_stay']:.1%} de maintien"
                    )

            assert True
        else:
            print(f"Response: {response.text[:500]}")
            assert False

    except Exception as e:
        print(f"❌ Erreur: {e}")
        assert False


@pytest.mark.skipif(
    not can_reach_api(),
    reason="API non accessible (tests d'intégration pour l'API déployée)",
)
def test_validation_errors():
    """Test des erreurs de validation."""
    print_section("6. TEST VALIDATION DES ERREURS")

    test_cases = [
        {
            "name": "Âge hors limites (> 60)",
            "data": {"age": 65, "genre": "M"},  # Données partielles invalides
            "expected_status": 422,
        },
        {
            "name": "Genre invalide",
            "data": {"age": 35, "genre": "X"},
            "expected_status": 422,
        },
        {
            "name": "Champs manquants",
            "data": {"age": 35, "genre": "M"},  # Manque plein de champs
            "expected_status": 422,
        },
        {
            "name": "nb_formations hors limites (> 6)",
            "data": {"age": 35, "nb_formations_suivies": 10},
            "expected_status": 422,
        },
    ]

    all_passed = True
    for test in test_cases:
        try:
            response = requests.post(
                f"{API_BASE_URL}/predict",
                json=test["data"],
                headers=HEADERS,
                timeout=30,
            )

            if response.status_code == test["expected_status"]:
                print(f"✅ {test['name']}: Status {response.status_code} (attendu)")
            else:
                print(
                    f"⚠️  {test['name']}: Status {response.status_code} (attendu: {test['expected_status']})"
                )
                all_passed = False

        except Exception as e:
            print(f"❌ {test['name']}: Erreur - {e}")
            all_passed = False

    assert all_passed


@pytest.mark.skipif(
    not can_reach_api(),
    reason="API non accessible (tests d'intégration pour l'API déployée)",
)
def test_all_postes():
    """Test avec différents postes pour vérifier l'impact."""
    print_section("7. TEST IMPACT DES DIFFÉRENTS POSTES")

    postes = [
        "Cadre Commercial",
        "Assistant de Direction",
        "Consultant",
        "Tech Lead",
        "Manager",
        "Senior Manager",
        "Représentant Commercial",
        "Directeur Technique",
        "Ressources Humaines",
    ]

    base_employee = {
        "nombre_participation_pee": 1,
        "nb_formations_suivies": 2,
        "nombre_employee_sous_responsabilite": 1,
        "distance_domicile_travail": 10,
        "niveau_education": 3,
        "domaine_etude": "Infra & Cloud",
        "ayant_enfants": "N",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 2,
        "annes_sous_responsable_actuel": 3,
        "satisfaction_employee_environnement": 3,
        "note_evaluation_precedente": 3,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Non",
        "augementation_salaire_precedente": 5.0,
        "age": 35,
        "genre": "M",
        "revenu_mensuel": 5000.0,
        "statut_marital": "Marié(e)",
        "departement": "Commercial",
        "poste": "Consultant",  # Sera remplacé
        "nombre_experiences_precedentes": 3,
        "nombre_heures_travailless": 80,
        "annee_experience_totale": 10,
        "annees_dans_l_entreprise": 5,
        "annees_dans_le_poste_actuel": 3,
    }

    print("📊 Probabilité de départ selon le poste (même profil de base):\n")

    results = []
    for poste in postes:
        employee = base_employee.copy()
        employee["poste"] = poste

        try:
            response = requests.post(
                f"{API_BASE_URL}/predict",
                json=employee,
                headers=HEADERS,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                results.append((poste, data["probability_1"], data["risk_level"]))
        except Exception:
            pass

    # Trier par risque décroissant
    results.sort(key=lambda x: x[1], reverse=True)

    for poste, prob, risk in results:
        risk_emoji = {"Low": "🟢", "Medium": "🟠", "High": "🔴"}.get(risk, "⚪")
        bar = "█" * int(prob * 20)
        print(f"   {risk_emoji} {poste:25s} {prob:5.1%} {bar}")

    assert len(results) > 0


def main():
    """Exécute tous les tests de démonstration."""
    print("\n" + "🚀" * 30)
    print("\n   DÉMONSTRATION API EMPLOYEE TURNOVER PREDICTION")
    print(f"   API: {API_BASE_URL}")
    print("\n" + "🚀" * 30)

    results = {
        "Endpoint racine": test_root_endpoint(),
        "Health check": test_health_endpoint(),
        "Prédiction unitaire": test_predict_single(),
        "Employé haut risque": test_predict_high_risk(),
        "Prédiction batch CSV": test_predict_batch(),
        "Validation erreurs": test_validation_errors(),
        "Impact des postes": test_all_postes(),
    }

    # Résumé final
    print_section("📋 RÉSUMÉ DES TESTS")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        emoji = "✅" if result else "❌"
        print(f"   {emoji} {test_name}")

    print(f"\n   Total: {passed}/{total} tests réussis")

    if passed == total:
        print("\n   🎉 Tous les tests ont réussi !")
        sys.exit(0)
    else:
        print(f"\n   ⚠️  {total - passed} test(s) échoué(s)")
        sys.exit(1)


if __name__ == "__main__":
    main()
