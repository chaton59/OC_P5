#!/usr/bin/env python3
"""
Test rapide MLflow avec n_iter=10 au lieu de 1000.
"""
import os

import mlflow
from sklearn.model_selection import RandomizedSearchCV

from ml_model.preprocess import preprocess_data
from ml_model.train_model import train_model

# Configure MLflow pour utiliser SQLite (nécessaire pour Model Registry)
mlflow.set_tracking_uri("sqlite:///mlflow.db")

# Patch temporaire pour test rapide
import ml_model.train_model as train_module

original_train = train_module.train_model


def quick_train(X, y):
    """Version rapide avec n_iter=10"""
    import mlflow
    import mlflow.sklearn
    from imblearn.over_sampling import SMOTE
    from imblearn.pipeline import Pipeline as ImbPipeline
    from scipy.stats import randint, uniform
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.model_selection import RandomizedSearchCV, train_test_split
    from xgboost import XGBClassifier

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    ratio = sum(y == 0) / sum(y == 1)

    pipeline = ImbPipeline(
        [("sampler", SMOTE(random_state=42)), ("clf", XGBClassifier(random_state=42))]
    )
    param_dist = {
        "clf__max_depth": randint(3, 15),
        "clf__n_estimators": randint(100, 1000),
        "clf__learning_rate": uniform(0.001, 0.5),
        "clf__subsample": uniform(0.4, 0.6),
        "clf__reg_alpha": uniform(0, 3),
        "clf__gamma": uniform(0, 10),
        "clf__colsample_bytree": uniform(0.5, 0.5),
        "clf__min_child_weight": randint(1, 15),
        "clf__scale_pos_weight": uniform(1, ratio),
        "clf__tree_method": ["auto", "hist"],
    }

    random = RandomizedSearchCV(
        pipeline,
        param_dist,
        n_iter=10,  # 🚀 Test rapide !
        cv=3,  # Réduit aussi le CV
        scoring="f1",
        n_jobs=-1,
        random_state=42,
    )

    with mlflow.start_run(run_name="XGBoost_Quick_Test"):
        random.fit(X_train, y_train)

        best_model = random.best_estimator_  # type: ignore[assignment]
        best_params = random.best_params_
        cv_f1 = random.best_score_

        mlflow.log_params(best_params)
        mlflow.log_metric("cv_f1", cv_f1)

        y_pred = best_model.predict(X_test)  # type: ignore[attr-defined]
        report = classification_report(y_test, y_pred, output_dict=True)  # type: ignore[arg-type]

        mlflow.log_metric("test_precision", float(report["1"]["precision"]))  # type: ignore[index]
        mlflow.log_metric("test_recall", float(report["1"]["recall"]))  # type: ignore[index]
        mlflow.log_metric("test_f1", float(report["1"]["f1-score"]))  # type: ignore[index]

        # Log model et enregistre dans Model Registry
        model_info = mlflow.sklearn.log_model(best_model, "model")  # type: ignore[attr-defined]
        mlflow.register_model(
            model_uri=model_info.model_uri, name="XGBoost_Employee_Turnover"
        )

        print("Meilleurs params:", best_params)
        print("Meilleur CV F1:", cv_f1)
        print(classification_report(y_test, y_pred))
        print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

    return best_model, best_params, cv_f1


if __name__ == "__main__":
    print("🔄 Chargement et prétraitement des données...")
    data_paths = {
        "sondage_path": "data/extrait_sondage.csv",
        "eval_path": "data/extrait_eval.csv",
        "sirh_path": "data/extrait_sirh.csv",
    }

    X, y, scaler, onehot, ordinal = preprocess_data(raw_data_paths=data_paths)
    print(f"✅ Données prétraitées :")
    print(f"   X shape: {X.shape}, y shape: {y.shape}")
    print(f"   Distribution y: {y.value_counts().to_dict()}")

    print("\n🚀 Lancement du test rapide (n_iter=10, cv=3)...\n")

    best_model, best_params, cv_f1 = quick_train(X, y)

    print(f"\n✅ Test terminé ! CV F1-score: {cv_f1:.4f}")

    print("\n📁 Vérification des artifacts MLflow dans ./mlruns :")
    if os.path.exists("./mlruns"):
        for root, dirs, files in os.walk("./mlruns"):
            level = root.replace("./mlruns", "").count(os.sep)
            if level < 3:  # Limite la profondeur
                indent = " " * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                if level == 2:  # Affiche fichiers dans les runs
                    subindent = " " * 2 * (level + 1)
                    for file in files[:3]:
                        print(f"{subindent}{file}")
                    if len(files) > 3:
                        print(f"{subindent}... (+{len(files) - 3} fichiers)")

    print("\n💡 Pour visualiser les runs MLflow, exécutez :")
    print("   mlflow ui")
    print("   Puis ouvrez http://localhost:5000")
