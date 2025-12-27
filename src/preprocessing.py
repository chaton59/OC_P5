#!/usr/bin/env python3
"""
Module de preprocessing pour transformer les données d'entrée avant prédiction.

Ce module applique les mêmes transformations que le pipeline d'entraînement :
- Feature engineering (ratios, moyennes)
- Encoding (OneHot, Ordinal)
- Scaling (StandardScaler avec paramètres sauvegardés)
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

from src.schemas import EmployeeInput

# Paramètres du scaler sauvegardés depuis l'entraînement
# Ces valeurs doivent correspondre exactement à celles utilisées lors du training
SCALER_PARAMS = {
    "columns": [
        "nombre_participation_pee",
        "nb_formations_suivies",
        "nombre_employee_sous_responsabilite",
        "distance_domicile_travail",
        "niveau_education",
        "annees_depuis_la_derniere_promotion",
        "annes_sous_responsable_actuel",
        "satisfaction_employee_environnement",
        "note_evaluation_precedente",
        "niveau_hierarchique_poste",
        "satisfaction_employee_nature_travail",
        "satisfaction_employee_equipe",
        "satisfaction_employee_equilibre_pro_perso",
        "note_evaluation_actuelle",
        "augementation_salaire_precedente",
        "age",
        "revenu_mensuel",
        "nombre_experiences_precedentes",
        "nombre_heures_travailless",
        "annee_experience_totale",
        "annees_dans_l_entreprise",
        "annees_dans_le_poste_actuel",
        "revenu_par_anciennete",
        "experience_par_anciennete",
        "satisfaction_moyenne",
        "promo_par_anciennete",
        "frequence_deplacement",
    ],
    "mean": [
        0.7938775510204081,
        2.7993197278911564,
        1.0,
        9.19251700680272,
        2.912925170068027,
        2.1789115646258503,
        4.102721088435374,
        2.721768707482993,
        2.7299319727891156,
        2.0639455782312925,
        2.7285714285714286,
        2.7122448979591836,
        2.7612244897959184,
        3.1537414965986397,
        15.209523809523809,
        36.923809523809524,
        6502.931292517007,
        2.6931972789115646,
        80.0,
        11.268707482993197,
        6.980272108843537,
        4.214965986394557,
        1170.0019803036198,
        1.9285635921785853,
        2.730952380952381,
        0.23624418065415922,
        1.0863945578231293,
    ],
    "scale": [
        0.8517867966287158,
        1.2888320187689346,
        1.0,
        8.104106529671768,
        1.0238165299102608,
        3.1873417003246085,
        3.502524756587405,
        1.0927103547111134,
        0.7113190741884202,
        1.1065633247112856,
        1.1024709415085499,
        1.0808410657505316,
        0.7062354909319911,
        0.3607007746349458,
        3.658692627979528,
        9.132265690615387,
        4706.355164823003,
        2.497159198593844,
        1.0,
        7.7078836108215345,
        6.0028580432875085,
        3.575242796407657,
        1353.331540788815,
        2.2050718706188372,
        0.5056427624070211,
        0.2687717006578023,
        0.5319888822661019,
    ],
}


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
        DataFrame transformé avec 50 colonnes dans l'ordre exact du modèle.
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

    # === RÉORDONNER LES COLONNES SELON L'ORDRE DU MODÈLE ===
    # Ordre exact des features attendues par le modèle (50 colonnes)
    expected_columns = [
        "nombre_participation_pee",
        "nb_formations_suivies",
        "nombre_employee_sous_responsabilite",
        "distance_domicile_travail",
        "niveau_education",
        "annees_depuis_la_derniere_promotion",
        "annes_sous_responsable_actuel",
        "satisfaction_employee_environnement",
        "note_evaluation_precedente",
        "niveau_hierarchique_poste",
        "satisfaction_employee_nature_travail",
        "satisfaction_employee_equipe",
        "satisfaction_employee_equilibre_pro_perso",
        "note_evaluation_actuelle",
        "augementation_salaire_precedente",
        "age",
        "revenu_mensuel",
        "nombre_experiences_precedentes",
        "nombre_heures_travailless",
        "annee_experience_totale",
        "annees_dans_l_entreprise",
        "annees_dans_le_poste_actuel",
        "revenu_par_anciennete",
        "experience_par_anciennete",
        "satisfaction_moyenne",
        "promo_par_anciennete",
        "genre_F",
        "genre_M",
        "statut_marital_Célibataire",
        "statut_marital_Divorcé(e)",
        "statut_marital_Marié(e)",
        "departement_Commercial",
        "departement_Consulting",
        "departement_Ressources Humaines",
        "poste_Assistant de Direction",
        "poste_Cadre Commercial",
        "poste_Consultant",
        "poste_Directeur Technique",
        "poste_Manager",
        "poste_Représentant Commercial",
        "poste_Ressources Humaines",
        "poste_Senior Manager",
        "poste_Tech Lead",
        "domaine_etude_Autre",
        "domaine_etude_Entrepreunariat",
        "domaine_etude_Infra & Cloud",
        "domaine_etude_Marketing",
        "domaine_etude_Ressources Humaines",
        "domaine_etude_Transformation Digitale",
        "frequence_deplacement",
    ]

    # Réordonner les colonnes
    df = df[expected_columns]

    # === SCALING ===
    # Appliquer le StandardScaler avec les paramètres sauvegardés
    for i, col in enumerate(SCALER_PARAMS["columns"]):
        if col in df.columns:
            mean = SCALER_PARAMS["mean"][i]
            scale = SCALER_PARAMS["scale"][i]
            df[col] = (df[col] - mean) / scale

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


def preprocess_dataframe_for_prediction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Préprocess un DataFrame complet (issu de CSV fusionnés) pour prédiction batch.

    Args:
        df: DataFrame avec toutes les colonnes nécessaires.

    Returns:
        DataFrame transformé prêt pour model.predict().
    """
    # Feature engineering
    df_processed = engineer_features(df)

    # Encoding et scaling
    df_processed = encode_and_scale(df_processed)

    return df_processed


def merge_csv_dataframes(
    sondage_df: pd.DataFrame,
    eval_df: pd.DataFrame,
    sirh_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Fusionne les 3 DataFrames CSV comme lors de l'entraînement.

    Args:
        sondage_df: DataFrame du fichier sondage.
        eval_df: DataFrame du fichier évaluation.
        sirh_df: DataFrame du fichier SIRH.

    Returns:
        DataFrame fusionné avec toutes les colonnes.
    """
    # Nettoyage de l'évaluation
    eval_df = eval_df.copy()
    eval_df["augementation_salaire_precedente"] = eval_df[
        "augementation_salaire_precedente"
    ].apply(lambda x: float(str(x).replace(" %", "")) if isinstance(x, str) else x)
    eval_df["employee_id"] = eval_df["eval_number"].apply(
        lambda x: int(str(x).replace("E_", "")) if isinstance(x, str) else x
    )

    # Nettoyage du sondage
    sondage_df = sondage_df.copy()
    sondage_df["employee_id"] = sondage_df["code_sondage"].apply(
        lambda x: int(x) if isinstance(x, (str, int)) else None
    )

    # Fusion
    central_df = pd.merge(sondage_df, eval_df, on="employee_id", how="inner")
    central_df = pd.merge(
        central_df, sirh_df, left_on="employee_id", right_on="id_employee", how="inner"
    )

    # Conserver l'ID pour le retour
    central_df["original_employee_id"] = central_df["employee_id"]

    # Supprimer les colonnes de jointure
    central_df.drop(
        ["code_sondage", "eval_number", "id_employee", "employee_id"],
        axis=1,
        inplace=True,
        errors="ignore",
    )

    return central_df
