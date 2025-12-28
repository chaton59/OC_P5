#!/usr/bin/env python3
"""
Script pour insérer le dataset complet dans PostgreSQL.

Ce script :
1. Lit les fichiers CSV (sondage, eval, sirh)
2. Fusionne les données selon les clés communes
3. Insère dans la table dataset de PostgreSQL
"""
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import get_settings


def load_csv_files():
    """Charge les fichiers CSV."""
    print("📂 Chargement des fichiers CSV...")

    # Chemins des fichiers
    data_dir = "data"
    sondage_file = os.path.join(data_dir, "extrait_sondage.csv")
    eval_file = os.path.join(data_dir, "extrait_eval.csv")
    sirh_file = os.path.join(data_dir, "extrait_sirh.csv")

    # Charger les dataframes
    df_sondage = pd.read_csv(sondage_file)
    df_eval = pd.read_csv(eval_file)
    df_sirh = pd.read_csv(sirh_file)

    print(f"✅ Sondage: {len(df_sondage)} lignes")
    print(f"✅ Évaluation: {len(df_eval)} lignes")
    print(f"✅ SIRH: {len(df_sirh)} lignes")

    return df_sondage, df_eval, df_sirh


def merge_datasets(df_sondage, df_eval, df_sirh):
    """Fusionne les datasets selon les clés communes."""
    print("🔗 Fusion des datasets...")

    # Les datasets semblent déjà avoir le même nombre de lignes et être dans le même ordre
    # On peut les concaténer horizontalement
    df_merged = pd.concat([df_sondage, df_eval, df_sirh], axis=1)

    # Supprimer les colonnes dupliquées si elles existent
    df_merged = df_merged.loc[:, ~df_merged.columns.duplicated()]

    print(
        f"✅ Dataset fusionné: {len(df_merged)} lignes, {len(df_merged.columns)} colonnes"
    )
    print(f"📊 Colonnes: {list(df_merged.columns)}")

    return df_merged


def prepare_for_db(df):
    """Prépare les données pour l'insertion en base."""
    print("🔧 Préparation des données pour la DB...")

    # Séparer les features et la target
    # La colonne 'a_quitte_l_entreprise' semble être la target (Oui/Non)
    target_col = "a_quitte_l_entreprise"

    if target_col in df.columns:
        features_df = df.drop(columns=[target_col])
        target_df = df[target_col]
    else:
        print(
            "⚠️ Colonne target non trouvée, utilisation de toutes les colonnes comme features"
        )
        features_df = df
        target_df = pd.Series(["Non"] * len(df))  # Valeur par défaut

    print(f"✅ Features: {len(features_df.columns)} colonnes")
    print(f"✅ Target: {len(target_df)} valeurs")

    return features_df, target_df


def insert_into_db(features_df, target_df, db_url):
    """Insère les données dans PostgreSQL."""
    print("💾 Insertion en base de données...")

    # Créer la connexion
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Importer le modèle
        from db_models import Dataset

        # Vider la table existante (optionnel, pour éviter les doublons)
        session.query(Dataset).delete()
        session.commit()
        print("🗑️ Table dataset vidée")

        # Insérer les données
        inserted_count = 0
        for idx, row in features_df.iterrows():
            # Convertir la ligne en dict JSON
            features_dict = row.to_dict()

            # Nettoyer les valeurs (remplacer NaN par None)
            features_dict = {
                k: (v if pd.notna(v) else None) for k, v in features_dict.items()
            }

            # Récupérer la target
            target = str(target_df.iloc[idx]) if idx < len(target_df) else "Non"

            # Créer l'enregistrement
            dataset_entry = Dataset(features_json=features_dict, target=target)

            session.add(dataset_entry)
            inserted_count += 1

            # Commit par batch de 100 pour performance
            if inserted_count % 100 == 0:
                session.commit()
                print(f"📊 {inserted_count} enregistrements insérés...")

        # Commit final
        session.commit()
        print(f"✅ Insertion terminée: {inserted_count} enregistrements")

    except Exception as e:
        session.rollback()
        print(f"❌ Erreur lors de l'insertion: {e}")
        raise
    finally:
        session.close()


def main():
    """Fonction principale."""
    print("🚀 Insertion du dataset complet dans PostgreSQL\n")

    try:
        # Charger la configuration
        settings = get_settings()
        db_url = settings.DATABASE_URL

        # Étape 1: Charger les CSV
        df_sondage, df_eval, df_sirh = load_csv_files()

        # Étape 2: Fusionner
        df_merged = merge_datasets(df_sondage, df_eval, df_sirh)

        # Étape 3: Préparer pour DB
        features_df, target_df = prepare_for_db(df_merged)

        # Étape 4: Insérer en DB
        insert_into_db(features_df, target_df, db_url)

        print("\n🎉 Dataset inséré avec succès !")
        print("📊 Vérifiez avec: SELECT COUNT(*) FROM dataset;")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
