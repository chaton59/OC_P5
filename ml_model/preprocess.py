import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from scipy.stats.mstats import winsorize
from scipy import stats


def load_raw_data(
    sondage_path="../raw_data/extrait_sondage.csv",
    eval_path="../raw_data/extrait_eval.csv",
    sirh_path="../raw_data/extrait_sirh.csv",
):
    """Charge et merge raw data (comme exploration.py/preparation.py)."""
    sondage = pd.read_csv(sondage_path)
    eval_df = pd.read_csv(eval_path)
    sirh = pd.read_csv(sirh_path)
    # Nettoyage initial (comme exploration.py)
    eval_df["augementation_salaire_precedente"] = eval_df[
        "augementation_salaire_precedente"
    ].apply(lambda x: float(str(x).replace(" %", "")) if isinstance(x, str) else x)
    eval_df["employee_id"] = eval_df["eval_number"].apply(
        lambda x: int(str(x).replace("E_", "")) if isinstance(x, str) else x
    )
    sondage["employee_id"] = sondage["code_sondage"].apply(
        lambda x: int(x) if isinstance(x, (str, int)) else None
    )
    # Merge (assume sur employee_id ; ajuste si clé diff.)
    central_df = pd.merge(sondage, eval_df, on="employee_id", how="inner")
    central_df = pd.merge(
        central_df, sirh, left_on="employee_id", right_on="id_employee", how="inner"
    )
    central_df.drop(
        ["code_sondage", "eval_number", "id_employee", "employee_id"],
        axis=1,
        inplace=True,
        errors="ignore",
    )
    return central_df


def preprocess_data(raw_data_paths=None):
    """
    Pipeline complet : Nettoyage, engineering, encoding, scaling (de preparation/improvement.py).
    Retourne X (features), y (binaire), scaler (pour inférence API).
    Choix : Sans PCA pour interprétabilité ; winsorize outliers (1%) ; OneHot cat. non-ordonnées.
    """
    if raw_data_paths:
        central_df = load_raw_data(**raw_data_paths)
    else:
        central_df = pd.read_csv("../output/central_df.csv")  # Si pré-fusionné

    # Nettoyage (duplicatas, constantes, outliers)
    central_df.drop_duplicates(inplace=True)
    columns_to_drop = (
        ["ayant_enfants"] if len(central_df["ayant_enfants"].unique()) == 1 else []
    )  # Constante
    central_df.drop(columns=columns_to_drop, inplace=True)
    quantitative_cols = central_df.select_dtypes(include=["int64", "float64"]).columns
    for col in quantitative_cols:
        if (
            central_df[col].std() > 0
            and np.sum(np.abs(stats.zscore(central_df[col])) > 3) > 0
        ):
            central_df[col] = winsorize(central_df[col], limits=[0.01, 0.01])

    # Engineering (comme improvement.py : ratios, moyennes ; +1 évite div0)
    central_df["revenu_par_anciennete"] = (
        central_df["revenu_mensuel"]
        / (central_df["annees_dans_l_entreprise"] + 1)
    )
    central_df["experience_par_anciennete"] = (
        central_df["annee_experience_totale"]
        / (central_df["annees_dans_l_entreprise"] + 1)
    )
    central_df["satisfaction_moyenne"] = central_df[
        [
            "satisfaction_employee_environnement",
            "satisfaction_employee_nature_travail",
            "satisfaction_employee_equipe",
            "satisfaction_employee_equilibre_pro_perso",
        ]
    ].mean(axis=1)
    # Autres (ajoute si pertinents via SHAP : e.g., 'promo_par_anciennete')
    central_df["promo_par_anciennete"] = (
        central_df["annees_depuis_la_derniere_promotion"]
        / (central_df["annees_dans_l_entreprise"] + 1)
    )

    # Encoding (catégorielles : OneHot non-ord., Ordinal ord.)
    cat_non_ord = ["genre", "statut_marital", "departement", "poste", "domaine_etude"]
    onehot = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    encoded_non_ord = pd.DataFrame(
        onehot.fit_transform(central_df[cat_non_ord]),
        columns=onehot.get_feature_names_out(cat_non_ord),
    )
    cat_ord = ["frequence_deplacement"]  # Ordinal : Aucun=0, Occasionnel=1, Frequent=2
    ordinal = OrdinalEncoder(categories=[["Aucun", "Occasionnel", "Frequent"]])
    encoded_ord = pd.DataFrame(
        ordinal.fit_transform(central_df[cat_ord]), columns=cat_ord
    )

    # Assemblage
    df_engineered = pd.concat(
        [
            central_df[quantitative_cols],
            encoded_non_ord,
            encoded_ord,
            central_df["a_quitte_l_entreprise"],
        ],
        axis=1,
    )  # Inclut cible

    # Scaling (quantitatives + ordinal)
    cols_to_scale = (
        quantitative_cols.tolist()
        + cat_ord
        + [
            "revenu_par_anciennete",
            "experience_par_anciennete",
            "satisfaction_moyenne",
            "promo_par_anciennete",
        ]
    )
    scaler = StandardScaler()
    df_engineered[cols_to_scale] = scaler.fit_transform(df_engineered[cols_to_scale])

    # Séparation X/y
    y = (df_engineered["a_quitte_l_entreprise"] == "Oui").astype(int)
    X = df_engineered.drop("a_quitte_l_entreprise", axis=1)
    return X, y, scaler, onehot, ordinal  # Retourne encoders/scaler pour inférence API
