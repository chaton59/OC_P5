import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from xgboost import XGBClassifier
from scipy.stats import uniform, randint

def train_model(X, y):
    """
    Train/tune XGBoost avec SMOTE (de optimisation.py/improvement.py).
    Retourne best_model, best_params, cv_f1.
    Choix : RandomizedSearch (efficace large grille) ; SMOTE in-pipeline (gère CV) ; F1 scoring (déséquilibre).
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    ratio = sum(y == 0) / sum(y == 1)
    
    pipeline = Pipeline([('sampler', SMOTE(random_state=42)), ('clf', XGBClassifier(random_state=42))])
    param_dist = {
        'clf__max_depth': randint(3, 15),
        'clf__n_estimators': randint(100, 1000),
        'clf__learning_rate': uniform(0.001, 0.5),
        'clf__subsample': uniform(0.4, 0.6),
        'clf__reg_alpha': uniform(0, 3),
        'clf__gamma': uniform(0, 10),
        'clf__colsample_bytree': uniform(0.5, 0.5),
        'clf__min_child_weight': randint(1, 15),
        'clf__scale_pos_weight': uniform(1, ratio),
        'clf__tree_method': ['auto', 'hist']  # CPU
    }
    
    random = RandomizedSearchCV(pipeline, param_dist, n_iter=1000, cv=5, scoring='f1', n_jobs=-1, random_state=42)
    random.fit(X_train, y_train)
    
    best_model = random.best_estimator_
    best_params = random.best_params_
    cv_f1 = random.best_score_
    
    # Éval test (pédagogique)
    y_pred = best_model.predict(X_test)
    print("Meilleurs params:", best_params)
    print("Meilleur CV F1:", cv_f1)
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
    
    return best_model, best_params, cv_f1