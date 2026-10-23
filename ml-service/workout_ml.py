"""
Shared ML code for the workout-plan service.

Everything that must be identical between training, evaluation and inference
lives here: feature names, allowed categories, BMI calculation, data
validation, the rule-based baseline and the scikit-learn pipelines.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "synthetic_workout_plans.csv"
ARTIFACT_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "workout_pipeline.joblib"
METADATA_PATH = ARTIFACT_DIR / "model_metadata.json"
REPORT_DIR = BASE_DIR / "reports"

RANDOM_SEED = 42
TEST_SIZE = 0.2

# Same limits the Express backend and React form enforce.
WEIGHT_RANGE_KG = (20.0, 300.0)
HEIGHT_RANGE_CM = (100.0, 250.0)

GOALS = ["Cut", "Bulk", "Maintain"]
EXPERIENCES = ["Beginner", "Intermediate", "Advanced"]

NUMERIC_FEATURES = ["Weight", "Height", "BMI"]
CATEGORICAL_FEATURES = ["Goal", "Experience"]
FEATURES = ["Weight", "Height", "BMI", "Goal", "Experience"]
TARGET = "Plan"

GOAL_TO_PLAN_PREFIX = {"Cut": "FatLoss", "Bulk": "MuscleGain", "Maintain": "Maintenance"}
PLANS = sorted(f"{GOAL_TO_PLAN_PREFIX[g]}_{e}" for g in GOALS for e in EXPERIENCES)


def compute_bmi(weight_kg, height_cm):
    """BMI = kg / m^2, rounded to 2 decimals (matches the original ml_api.py)."""
    height_m = np.asarray(height_cm, dtype=float) / 100
    return np.round(np.asarray(weight_kg, dtype=float) / height_m ** 2, 2)


def build_features(weight, height, goal, experience):
    """Single-row feature frame used at inference time."""
    return pd.DataFrame(
        [[float(weight), float(height), float(compute_bmi(weight, height)), goal, experience]],
        columns=FEATURES,
    )


def rule_based_plan(goal, experience):
    """Transparent baseline: the plan is the Goal x Experience lookup."""
    return f"{GOAL_TO_PLAN_PREFIX[goal]}_{experience}"


class DataValidationError(ValueError):
    pass


def validate_dataset(df):
    """
    Check schema, types, missing values, categories, ranges and BMI consistency.
    Raises DataValidationError listing every problem found.
    """
    problems = []

    missing_cols = [c for c in FEATURES + [TARGET] if c not in df.columns]
    if missing_cols:
        raise DataValidationError(f"Missing columns: {missing_cols}")

    n_missing = df[FEATURES + [TARGET]].isna().sum()
    if n_missing.any():
        problems.append(f"Missing values: {n_missing[n_missing > 0].to_dict()}")

    for col in NUMERIC_FEATURES:
        if not pd.api.types.is_numeric_dtype(df[col]):
            problems.append(f"Column '{col}' is not numeric (dtype {df[col].dtype})")

    if not problems:
        w_lo, w_hi = WEIGHT_RANGE_KG
        h_lo, h_hi = HEIGHT_RANGE_CM
        if not df["Weight"].between(w_lo, w_hi).all():
            problems.append(f"Weight outside [{w_lo}, {w_hi}] kg")
        if not df["Height"].between(h_lo, h_hi).all():
            problems.append(f"Height outside [{h_lo}, {h_hi}] cm")
        bmi_gap = (df["BMI"] - compute_bmi(df["Weight"], df["Height"])).abs()
        if (bmi_gap > 0.011).any():
            problems.append(f"{int((bmi_gap > 0.011).sum())} rows have BMI inconsistent with Weight/Height")

    for col, allowed in [("Goal", GOALS), ("Experience", EXPERIENCES), (TARGET, PLANS)]:
        bad = sorted(set(df[col].dropna().astype(str)) - set(allowed))
        if bad:
            problems.append(f"Unknown values in '{col}': {bad}")

    if problems:
        raise DataValidationError("; ".join(problems))


def data_quality_summary(df):
    """Duplicates, conflicting duplicates and class balance, as plain numbers."""
    counts = df[TARGET].value_counts().reindex(PLANS, fill_value=0)
    conflicting = df.groupby(FEATURES)[TARGET].nunique()
    return {
        "n_rows": int(len(df)),
        "n_exact_duplicate_rows": int(df.duplicated().sum()),
        "n_feature_vectors_with_conflicting_labels": int((conflicting > 1).sum()),
        "class_counts": {k: int(v) for k, v in counts.items()},
        "imbalance_ratio_max_over_min": round(float(counts.max() / max(counts.min(), 1)), 3),
    }


def load_dataset(path=DATA_PATH):
    """Load, validate and de-duplicate the dataset (duplicates dropped before splitting)."""
    df = pd.read_csv(path)
    validate_dataset(df)
    return df.drop_duplicates().reset_index(drop=True)


def split_dataset(df):
    """Reproducible stratified train/test split shared by training and evaluation."""
    return train_test_split(
        df[FEATURES], df[TARGET], test_size=TEST_SIZE, stratify=df[TARGET], random_state=RANDOM_SEED
    )


class RuleBasedClassifier(ClassifierMixin, BaseEstimator):
    """Scikit-learn compatible wrapper around rule_based_plan (learns nothing)."""

    def fit(self, X, y):
        self.classes_ = np.array(PLANS)
        return self

    def predict(self, X):
        return np.array([rule_based_plan(g, e) for g, e in zip(X["Goal"], X["Experience"])])


def _encoder(categorical, numeric, scale_numeric):
    # Goal is nominal, so it is one-hot encoded instead of given an arbitrary
    # integer order. Experience is one-hot too: each level maps to its own plan
    # template, so no equal spacing between levels is assumed.
    transformers = []
    if categorical:
        cats = [{"Goal": GOALS, "Experience": EXPERIENCES}[c] for c in categorical]
        transformers.append(("cat", OneHotEncoder(categories=cats, handle_unknown="error"), categorical))
    if numeric:
        transformers.append(("num", StandardScaler() if scale_numeric else "passthrough", numeric))
    return ColumnTransformer(transformers)


def make_decision_tree(categorical=CATEGORICAL_FEATURES, numeric=NUMERIC_FEATURES):
    return Pipeline([
        ("preprocess", _encoder(categorical, numeric, scale_numeric=False)),
        ("model", DecisionTreeClassifier(random_state=RANDOM_SEED)),
    ])


def make_random_forest(categorical=CATEGORICAL_FEATURES, numeric=NUMERIC_FEATURES):
    return Pipeline([
        ("preprocess", _encoder(categorical, numeric, scale_numeric=False)),
        ("model", RandomForestClassifier(n_estimators=100, random_state=RANDOM_SEED)),
    ])


def make_logistic_regression(categorical=CATEGORICAL_FEATURES, numeric=NUMERIC_FEATURES):
    return Pipeline([
        ("preprocess", _encoder(categorical, numeric, scale_numeric=True)),
        ("model", LogisticRegression(max_iter=2000, random_state=RANDOM_SEED)),
    ])


# Candidates for model selection. Baselines are reference points only; the
# deployed model is chosen from the learned candidates, which are listed from
# simplest to most complex: fewer input features first, then single tree <
# linear model < 100-tree ensemble.
TIE_TOLERANCE = 0.005


def baseline_candidates():
    return {
        "dummy_most_frequent": DummyClassifier(strategy="most_frequent"),
        "dummy_stratified": DummyClassifier(strategy="stratified", random_state=RANDOM_SEED),
        "rule_lookup": RuleBasedClassifier(),
    }


def learned_candidates():
    return {
        "decision_tree_goal_experience": make_decision_tree(numeric=[]),
        "logistic_regression_goal_experience": make_logistic_regression(numeric=[]),
        "random_forest_goal_experience": make_random_forest(numeric=[]),
        "random_forest_numeric_only": make_random_forest(categorical=[]),
        "logistic_regression_all_features": make_logistic_regression(),
        "random_forest_all_features": make_random_forest(),
    }


def select_model(X_train, y_train):
    """
    Stratified 5-fold CV on the training split only. Returns per-candidate
    scores and the name of the simplest learned candidate whose mean macro-F1
    is within TIE_TOLERANCE of the best learned candidate.
    """
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    learned = learned_candidates()
    results = {}
    for name, model in {**baseline_candidates(), **learned}.items():
        scores = cross_validate(model, X_train, y_train, cv=cv, scoring=["accuracy", "f1_macro"])
        results[name] = {
            "type": "learned" if name in learned else "baseline",
            "cv_accuracy_mean": round(float(scores["test_accuracy"].mean()), 4),
            "cv_accuracy_std": round(float(scores["test_accuracy"].std()), 4),
            "cv_macro_f1_mean": round(float(scores["test_f1_macro"].mean()), 4),
            "cv_macro_f1_std": round(float(scores["test_f1_macro"].std()), 4),
        }
    best = max(results[n]["cv_macro_f1_mean"] for n in learned)
    selected = next(n for n in learned if results[n]["cv_macro_f1_mean"] >= best - TIE_TOLERANCE)
    return results, selected, learned[selected]
