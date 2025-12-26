#!/usr/bin/env python3
"""
Schémas Pydantic pour validation des données d'entrée de l'API.

Ces schémas correspondent aux colonnes brutes du dataset avant preprocessing,
permettant une validation stricte des inputs avec messages d'erreur clairs.
"""
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# Enums pour les valeurs catégorielles
class GenreEnum(str, Enum):
    """Genre de l'employé."""

    M = "M"
    F = "F"


class StatutMaritalEnum(str, Enum):
    """Statut marital de l'employé."""

    CELIBATAIRE = "Célibataire"
    MARIE = "Marié(e)"
    DIVORCE = "Divorcé(e)"


class DepartementEnum(str, Enum):
    """Département de l'employé."""

    COMMERCIAL = "Commercial"
    CONSULTING = "Consulting"


class DomaineEtudeEnum(str, Enum):
    """Domaine d'études de l'employé."""

    INFRA_CLOUD = "Infra & Cloud"
    TRANSFORMATION_DIGITALE = "Transformation Digitale"
    AUTRE = "Autre"


class FrequenceDeplacementEnum(str, Enum):
    """Fréquence des déplacements professionnels."""

    AUCUN = "Aucun"
    OCCASIONNEL = "Occasionnel"
    FREQUENT = "Frequent"


class EmployeeInput(BaseModel):
    """
    Schéma de validation pour les données d'entrée d'un employé.

    Tous les champs correspondent aux colonnes brutes des 3 fichiers CSV
    (sondage, eval, sirh) avant preprocessing.
    """

    # === Données SONDAGE ===
    nombre_participation_pee: int = Field(
        ..., ge=0, description="Nombre de participations au PEE"
    )
    nb_formations_suivies: int = Field(
        ..., ge=0, le=10, description="Nombre de formations suivies"
    )
    nombre_employee_sous_responsabilite: int = Field(
        ..., ge=0, description="Nombre d'employés sous responsabilité"
    )
    distance_domicile_travail: int = Field(
        ..., ge=0, le=50, description="Distance domicile-travail en km"
    )
    niveau_education: int = Field(
        ..., ge=1, le=5, description="Niveau d'éducation (1-5)"
    )
    domaine_etude: DomaineEtudeEnum = Field(..., description="Domaine d'études")
    ayant_enfants: Literal["Y", "N"] = Field(..., description="A des enfants (Y/N)")
    frequence_deplacement: FrequenceDeplacementEnum = Field(
        ..., description="Fréquence des déplacements"
    )
    annees_depuis_la_derniere_promotion: int = Field(
        ..., ge=0, description="Années depuis la dernière promotion"
    )
    annes_sous_responsable_actuel: int = Field(
        ..., ge=0, description="Années sous le responsable actuel"
    )

    # === Données EVALUATION ===
    satisfaction_employee_environnement: int = Field(
        ..., ge=1, le=4, description="Satisfaction environnement (1-4)"
    )
    note_evaluation_precedente: int = Field(
        ..., ge=1, le=5, description="Note évaluation précédente (1-5)"
    )
    niveau_hierarchique_poste: int = Field(
        ..., ge=1, le=5, description="Niveau hiérarchique (1-5)"
    )
    satisfaction_employee_nature_travail: int = Field(
        ..., ge=1, le=4, description="Satisfaction nature du travail (1-4)"
    )
    satisfaction_employee_equipe: int = Field(
        ..., ge=1, le=4, description="Satisfaction équipe (1-4)"
    )
    satisfaction_employee_equilibre_pro_perso: int = Field(
        ..., ge=1, le=4, description="Satisfaction équilibre pro/perso (1-4)"
    )
    note_evaluation_actuelle: int = Field(
        ..., ge=1, le=5, description="Note évaluation actuelle (1-5)"
    )
    heure_supplementaires: Literal["Oui", "Non"] = Field(
        ..., description="Fait des heures supplémentaires"
    )
    augementation_salaire_precedente: float = Field(
        ..., ge=0, le=100, description="Augmentation salaire précédente (%)"
    )

    # === Données SIRH ===
    age: int = Field(..., ge=18, le=70, description="Âge de l'employé")
    genre: GenreEnum = Field(..., description="Genre")
    revenu_mensuel: float = Field(..., ge=1000, description="Revenu mensuel (€)")
    statut_marital: StatutMaritalEnum = Field(..., description="Statut marital")
    departement: DepartementEnum = Field(..., description="Département")
    poste: str = Field(..., min_length=3, description="Intitulé du poste")
    nombre_experiences_precedentes: int = Field(
        ..., ge=0, description="Nombre d'expériences précédentes"
    )
    nombre_heures_travailless: int = Field(
        ..., ge=35, le=80, description="Nombre d'heures travaillées par semaine"
    )
    annee_experience_totale: int = Field(
        ..., ge=0, description="Années d'expérience totale"
    )
    annees_dans_l_entreprise: int = Field(
        ..., ge=0, description="Années dans l'entreprise"
    )
    annees_dans_le_poste_actuel: int = Field(
        ..., ge=0, description="Années dans le poste actuel"
    )

    @field_validator("augementation_salaire_precedente")
    @classmethod
    def validate_augmentation(cls, v: float) -> float:
        """Nettoie le format de l'augmentation (enlève % si présent)."""
        if isinstance(v, str):
            v = float(v.replace(" %", "").replace("%", ""))
        return v

    class Config:
        """Configuration Pydantic."""

        json_schema_extra = {
            "example": {
                # Exemple basé sur la première ligne des CSV
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
        }


class PredictionOutput(BaseModel):
    """Schéma de sortie pour les prédictions."""

    prediction: int = Field(..., description="Classe prédite (0=reste, 1=part)")
    probability_0: float = Field(
        ..., ge=0, le=1, description="Probabilité de rester (classe 0)"
    )
    probability_1: float = Field(
        ..., ge=0, le=1, description="Probabilité de partir (classe 1)"
    )
    risk_level: str = Field(..., description="Niveau de risque (Low/Medium/High)")

    class Config:
        """Configuration Pydantic."""

        json_schema_extra = {
            "example": {
                "prediction": 1,
                "probability_0": 0.35,
                "probability_1": 0.65,
                "risk_level": "High",
            }
        }


class HealthCheck(BaseModel):
    """Schéma pour le endpoint health check."""

    status: str = Field(..., description="Status de l'API")
    model_loaded: bool = Field(..., description="Modèle chargé ou non")
    model_type: str = Field(..., description="Type du modèle")
    version: str = Field(..., description="Version de l'API")

    class Config:
        """Configuration Pydantic."""

        json_schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "model_type": "Pipeline",
                "version": "1.0.0",
            }
        }
