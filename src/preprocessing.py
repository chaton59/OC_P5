#!/usr/bin/env python3
"""
Module de preprocessing pour transformer les données d'entrée avant prédiction.

Ce module applique les mêmes transformations que le pipeline d'entraînement :
- Feature engineering (ratios, moyennes)
- Encoding (OneHot, Ordinal)
- Scaling (StandardScaler)
"""
import numpy as np
import pandas as pd
from scipy.stats.mstats import winsorize
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

from src.schemas import EmployeeInput


def create_input_dataframe(employee: EmployeeInput) -> pd.DataFrame:
    """
    Convertit un objet EmployeeInput Pydantic en DataFrame pandas.

    Args:
        employee: Données validées d'un employé.

    Returns:
        DataFrame avec une seule ligne contenant toutes les features.
    """
    data = {
        # SONDAGE
        "nombre_participation_pee": [employee.nombre_participation_pee],
        "nb_formations_suivies": [employee.nb_formations_suivies],
        "nombre_employee_sous_responsabilite": [
            employee.nombre_employee_sous_responsabilite
        ],
        "distance_domicile_travail": [employee.distance_domicile_travail],
        "niveau_education": [employee.niveau_education],
        "domaine_etude": [employee.domaine_etude],
        "ayant_enfants": [employee.ayant_enfants],
        "frequence_deplacement": [employee.frequence_deplacement],
        "annees_depuis_la_derniere_promotion": [
            employee.annees_depuis_la_derniere_promotion
        ],
        "annes_sous_responsable_actuel": [employee.annes_sous_responsable_actuel],
        # EVALUATION
        "satisfaction_employee_environnement": [
            employee.satisfaction_employee_environnement
        ],
        "note_evaluation_precedente": [employee.note_evaluation_precedente],
        "niveau_hierarchique_poste": [employee.niveau_hierarchique_poste],
        "satisfaction_employee_nature_travail": [
            employee.satisfaction_employee_nature_travail
        ],
        "satisfaction_employee_equipe": [employee.satisfaction_employee_equipe],
        "satisfaction_employee_equilibre_pro_perso": [
            employee.satisfaction_employee_equilibre_pro_perso
        ],
        "note_evaluation_actuelle": [employee.note_evaluation_actuelle],
        "heure_supplementaires": [employee.heure_supplementaires],
        "augementation_salaire_precedente": [employee.augementation_salaire_precedente],
        # SIRH
        "age": [employee.age],
        "genre": [employee.genre],
        "revenu_mensuel": [employee.revenu_mensuel],
        "statut_marital": [employee.statut_marital],
        "departement": [employee.departement],
        "poste": [employee.poste],
        "nombre_experiences_precedentes": [employee.nombre_experiences_precedentes],
        "nombre_heures_travailless": [employee.nombre_heures_travailless],
        "annee_experience_totale": [employee.annee_experience_totale],
        "annees_dans_l_entreprise": [employee.annees_dans_l_entreprise],
        "annees_dans_le_poste_actuel": [employee.annees_dans_le_poste_actuel],
    }

    return pd.DataFrame(data)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique le feature engineering (mêmes transformations que l'entraînement).

    Args:
        df: DataFrame avec les colonnes brutes.

    Returns:
        DataFrame avec les features engineered ajoutées.
    """
    df = df.copy()

    # Ratios (+ 1 pour éviter division par zéro)
    df["revenu_par_anciennete"] = df["revenu_mensuel"] / (
        df["annees_dans_l_entreprise"] + 1
    )
    df["experience_par_anciennete"] = df["annee_experience_totale"] / (
        df["annees_dans_l_entreprise"] + 1
    )
    df["promo_par_anciennete"] = df["annees_depuis_la_derniere_promotion"] / (
        df["annees_dans_l_entreprise"] + 1
    )

    # Moyenne de satisfaction
    df["satisfaction_moyenne"] = df[
        [
            "satisfaction_employee_environnement",
            "satisfaction_employee_nature_travail",
            "satisfaction_employee_equipe",
            "satisfaction_employee_equilibre_pro_perso",
        ]
    ].mean(axis=1)

    return df


def encode_and_scale(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode les variables catégorielles et scale les numériques.
    IMPORTANT: Doit correspondre EXACTEMENT au pipeline d'entraînement.

    Args:
        df: DataFrame avec features engineered.

    Returns:
        DataFrame transformé avec 50 colonnes (comme training).
    """
    df = df.copy()

    # === ENCODING ===

    # NOTE: ayant_enfants et heure_supplementaires sont SUPPRIMÉS
    # (ne font pas partie des features du modèle d'entraînement)
    cols_to_drop = ["ayant_enfants", "heure_supplementaires"]
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    # OneHot pour variables catégorielles non-ordonnées
    # IMPORTANT: Utiliser les mêmes catégories que lors de l'entraînement
    cat_non_ord = ["genre", "statut_marital", "departement", "poste", "domaine_etude"]

    # Définir toutes les catégories possibles (depuis training data)
    categories_dict = {
        "genre": ["F", "M"],
        "statut_marital": ["Célibataire", "Divorcé(e)", "Marié(e)"],
        "departement": ["Commercial", "Consulting", "Ressources Humaines"],
        "poste": [
            "Assistant de Direction",
            "Cadre Commercial",
            "Consultant",
            "Directeur Technique",
            "Manager",
            "Représentant Commercial",
            "Ressources Humaines",
            "Senior Manager",
            "Tech Lead",
        ],
        "domaine_etude": [
            "Autre",
            "Entrepreunariat",
            "Infra & Cloud",
            "Marketing",
            "Ressources Humaines",
            "Transformation Digitale",
        ],
    }

    onehot = OneHotEncoder(
        sparse_output=False,
        handle_unknown="ignore",
        categories=[categories_dict[col] for col in cat_non_ord],
    )

    encoded_non_ord = pd.DataFrame(
        onehot.fit_transform(df[cat_non_ord]),
        columns=onehot.get_feature_names_out(cat_non_ord),
        index=df.index,
    )

    # Ordinal pour fréquence déplacement
    ordinal = OrdinalEncoder(categories=[["Aucun", "Occasionnel", "Frequent"]])
    df["frequence_deplacement"] = ordinal.fit_transform(
        df[["frequence_deplacement"]]
    ).flatten()

    # Supprimer les colonnes catégorielles originales
    df = df.drop(columns=cat_non_ord)

    # Concaténer les encodages OneHot
    df = pd.concat([df, encoded_non_ord], axis=1)

    # === SCALING ===

    # Colonnes numériques à scaler
    quantitative_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Retirer les colonnes OneHot du scaling (elles sont déjà 0/1)
    cols_to_scale = [
        col
        for col in quantitative_cols
        if df[col].nunique() > 2  # Exclut colonnes binaires (0/1)
    ]

    # Appliquer le scaling uniquement s'il y a des colonnes
    if cols_to_scale:
        scaler = StandardScaler()
        df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])

    return df


def preprocess_for_prediction(employee: EmployeeInput) -> np.ndarray:
    """
    Pipeline complet de preprocessing pour une prédiction.

    Args:
        employee: Données validées d'un employé.

    Returns:
        Array numpy transformé prêt pour model.predict().

    Examples:
        >>> from src.schemas import EmployeeInput
        >>> employee = EmployeeInput(...)
        >>> X = preprocess_for_prediction(employee)
        >>> prediction = model.predict(X)
    """
    # 1. Créer DataFrame
    df = create_input_dataframe(employee)

    # 2. Feature engineering
    df = engineer_features(df)

    # 3. Encoding et scaling
    df = encode_and_scale(df)

    # 4. Convertir en numpy array (le modèle attend un array)
    return df.values


# TODO: Implémenter le chargement des artifacts sauvegardés
# def load_preprocessing_artifacts(run_id: str) -> dict:
#     """
#     Charge les encoders et scaler depuis MLflow.
#
#     Returns:
#         dict avec keys: 'onehot_encoder', 'ordinal_encoder', 'scaler'
#     """
#     pass
