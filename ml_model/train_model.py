import mlflow
import mlflow.sklearn
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from scipy.stats import randint, uniform
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from xgboost import XGBClassifier


def train_model(X, y):
    """
    Train/tune XGBoost avec SMOTE (de optimisation.py/improvement.py).
    Retourne best_model, best_params, cv_f1.
    Choix : RandomizedSearch (efficace large grille) ; SMOTE in-pipeline (gère CV) ; F1 scoring (déséquilibre).
    """
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
        "clf__tree_method": ["auto", "hist"],  # CPU
    }

    random = RandomizedSearchCV(
        pipeline,
        param_dist,
        n_iter=1000,
        cv=5,
        scoring="f1",
        n_jobs=-1,
        random_state=42,
    )

    # Ajout MLflow : Encapsule training pour tracking auto (./mlruns)
    with mlflow.start_run(run_name="XGBoost_Tuning"):
        random.fit(X_train, y_train)

        best_model = random.best_estimator_  # type: ignore[assignment]
        best_params = random.best_params_
        cv_f1 = random.best_score_

        mlflow.log_params(
            best_params
        )  # Choix : Log tous hyperparams pour reproductibilité.
        mlflow.log_metric(
            "cv_f1", cv_f1
        )  # Choix : Métrique clé (F1 CV pour déséquilibre).

        y_pred = best_model.predict(X_test)  # type: ignore[attr-defined]
        report = classification_report(y_test, y_pred, output_dict=True)  # type: ignore[arg-type]

        # Type ignore car classification_report avec output_dict=True retourne dict, pas str
        mlflow.log_metric("test_precision", float(report["1"]["precision"]))  # type: ignore[index]
        mlflow.log_metric("test_recall", float(report["1"]["recall"]))  # type: ignore[index]
        mlflow.log_metric("test_f1", float(report["1"]["f1-score"]))  # type: ignore[index]

        mlflow.sklearn.log_model(best_model, "model")  # type: ignore[attr-defined]

        # Éval test (pédagogique)
        print("Meilleurs params:", best_params)
        print("Meilleur CV F1:", cv_f1)
        print(classification_report(y_test, y_pred))
        print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

    return best_model, best_params, cv_f1
