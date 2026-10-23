"""
Evaluate the trained workout-plan model.

1. Label audit       - is the target a deterministic function of Goal x Experience?
2. Held-out test     - the saved model, the rule baseline and a dummy baseline,
                       evaluated once on the untouched test split.
3. Feature relevance - a random forest given all five features is fitted on the
                       training split; permutation importance (single and
                       grouped) on the test split shows what each feature adds.
4. Input sweep       - does changing only Weight/Height ever change the served
                       model's prediction anywhere in the API's accepted range?

Model-selection (cross-validation) results are read from the metadata written
by train_model.py, so the test split is never used to choose a model.
Results are written to reports/evaluation_results.json.

Usage:  python evaluate_model.py        (run train_model.py first)
"""

import itertools
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score,
)
from sklearn.tree import export_text

from workout_ml import (
    CATEGORICAL_FEATURES, EXPERIENCES, FEATURES, GOALS, HEIGHT_RANGE_CM, METADATA_PATH, MODEL_PATH,
    NUMERIC_FEATURES, PLANS, RANDOM_SEED, REPORT_DIR, TARGET, WEIGHT_RANGE_KG, RuleBasedClassifier,
    compute_bmi, load_dataset, make_random_forest, rule_based_plan, split_dataset,
)


def r4(x):
    return round(float(x), 4)


def label_audit(df):
    cell_labels = df.groupby(CATEGORICAL_FEATURES)[TARGET].nunique()
    rule = [rule_based_plan(g, e) for g, e in zip(df["Goal"], df["Experience"])]
    return {
        "max_distinct_labels_per_goal_experience_cell": int(cell_labels.max()),
        "label_is_deterministic_in_goal_and_experience": bool(cell_labels.max() == 1),
        "fraction_rows_matching_rule": r4(np.mean(np.array(rule) == df[TARGET].to_numpy())),
    }


def holdout_metrics(y_true, y_pred):
    return {
        "accuracy": r4(accuracy_score(y_true, y_pred)),
        "macro_precision": r4(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "macro_recall": r4(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "macro_f1": r4(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }


def per_class_report(y_true, y_pred):
    report = classification_report(y_true, y_pred, labels=PLANS, output_dict=True, zero_division=0)
    return {c: {k: r4(v) for k, v in report[c].items()} for c in PLANS}


def grouped_numeric_permutation(model, X, y, n_repeats=20):
    """Shuffle Weight, Height and BMI together so their correlation is preserved."""
    rng = np.random.default_rng(RANDOM_SEED)
    base = f1_score(y, model.predict(X), average="macro")
    drops = []
    for _ in range(n_repeats):
        Xp = X.copy()
        Xp[NUMERIC_FEATURES] = X[NUMERIC_FEATURES].to_numpy()[rng.permutation(len(X))]
        drops.append(base - f1_score(y, model.predict(Xp), average="macro"))
    return {"mean": r4(np.mean(drops)), "std": r4(np.std(drops))}


def feature_relevance(X_train, y_train, X_test, y_test):
    """Give a random forest every feature, then measure what each one contributes on held-out data."""
    rf = make_random_forest().fit(X_train, y_train)
    perm = permutation_importance(rf, X_test, y_test, scoring="f1_macro", n_repeats=20, random_state=RANDOM_SEED)
    names = rf.named_steps["preprocess"].get_feature_names_out()
    return {
        "model": "random_forest_all_features, fitted on the training split",
        "permutation_importance_macro_f1_drop": {
            f: {"mean": r4(m), "std": r4(s)}
            for f, m, s in zip(FEATURES, perm.importances_mean, perm.importances_std)
        },
        "grouped_numeric_permutation_macro_f1_drop": grouped_numeric_permutation(rf, X_test, y_test),
        "impurity_importance": {
            n.split("__", 1)[1]: r4(v) for n, v in zip(names, rf.named_steps["model"].feature_importances_)
        },
    }


def input_grid(step=2.0):
    """Every Goal x Experience with Weight/Height spanning the full range the API accepts."""
    w = np.arange(WEIGHT_RANGE_KG[0], WEIGHT_RANGE_KG[1] + 1e-9, step)
    h = np.arange(HEIGHT_RANGE_CM[0], HEIGHT_RANGE_CM[1] + 1e-9, step)
    ww, hh = (a.ravel() for a in np.meshgrid(w, h))
    frames = []
    for g, e in itertools.product(GOALS, EXPERIENCES):
        frames.append(pd.DataFrame({"Weight": ww, "Height": hh, "BMI": compute_bmi(ww, hh), "Goal": g, "Experience": e}))
    return pd.concat(frames, ignore_index=True)[FEATURES]


def input_sweep(model, grid):
    """Does changing only Weight/Height/BMI ever change the predicted plan?"""
    pred = np.asarray(model.predict(grid))
    rule = np.array([rule_based_plan(g, e) for g, e in zip(grid["Goal"], grid["Experience"])])
    distinct = pd.Series(pred).groupby([grid["Goal"], grid["Experience"]]).nunique()
    return {
        "grid_points": int(len(grid)),
        "max_distinct_plans_within_a_goal_experience_cell": int(distinct.max()),
        "predictions_differing_from_rule": int((pred != rule).sum()),
    }


def describe_model(pipeline):
    est = pipeline.named_steps["model"]
    names = [n.split("__", 1)[1] for n in pipeline.named_steps["preprocess"].get_feature_names_out()]
    info = {"estimator": type(est).__name__, "features_used": names}
    if hasattr(est, "tree_"):
        info.update(depth=int(est.get_depth()), leaves=int(est.get_n_leaves()),
                    rules=export_text(est, feature_names=names))
    return info


def evaluate(model_path=MODEL_PATH, metadata_path=METADATA_PATH, out_dir=REPORT_DIR, grid_step=2.0):
    df = load_dataset()
    X_train, X_test, y_train, y_test = split_dataset(df)
    deployed = joblib.load(model_path)
    metadata = json.loads(metadata_path.read_text())

    y_deployed = deployed.predict(X_test)
    y_rule = RuleBasedClassifier().fit(X_train, y_train).predict(X_test)
    y_dummy = DummyClassifier(strategy="stratified", random_state=RANDOM_SEED).fit(X_train, y_train).predict(X_test)

    results = {
        "dataset": {"type": "SYNTHETIC", "rows_after_dedup": int(len(df)),
                    "train_rows": int(len(X_train)), "test_rows": int(len(X_test))},
        "label_audit": label_audit(df),
        "model_selection": {
            "selected_model": metadata["selected_model"],
            "selection_rule": metadata["selection_rule"],
            "cross_validation_on_train_split": metadata["cross_validation"],
        },
        "deployed_model": describe_model(deployed),
        "holdout_test": {
            "deployed_model": holdout_metrics(y_test, y_deployed),
            "rule_baseline": holdout_metrics(y_test, y_rule),
            "dummy_stratified": holdout_metrics(y_test, y_dummy),
            "deployed_vs_rule_agreement": r4(np.mean(y_deployed == y_rule)),
            "deployed_per_class": per_class_report(y_test, y_deployed),
            "deployed_confusion_matrix": {"labels": PLANS,
                                          "matrix": confusion_matrix(y_test, y_deployed, labels=PLANS).tolist()},
        },
        "feature_relevance": feature_relevance(X_train, y_train, X_test, y_test),
        "input_sweep_deployed_model": input_sweep(deployed, input_grid(grid_step)),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "evaluation_results.json").write_text(json.dumps(results, indent=2))
    return results


def main():
    res = evaluate()
    print("Dataset: SYNTHETIC |", res["dataset"])
    print("Label audit:", res["label_audit"])
    sel = res["model_selection"]
    print("\n5-fold CV on the training split (from train_model.py), macro-F1:")
    for name, r in sel["cross_validation_on_train_split"].items():
        print(f"  [{r['type']:8s}] {name:38s} {r['cv_macro_f1_mean']:.4f} +/- {r['cv_macro_f1_std']:.4f}")
    print("Selected:", sel["selected_model"])
    dm = res["deployed_model"]
    print(f"\nDeployed model: {dm['estimator']} on {dm['features_used']}"
          + (f", depth {dm['depth']}, {dm['leaves']} leaves" if "depth" in dm else ""))
    ho = res["holdout_test"]
    print("\nHeld-out test:")
    for k in ["deployed_model", "rule_baseline", "dummy_stratified"]:
        print(f"  {k:18s}", ho[k])
    print("  deployed vs rule agreement:", ho["deployed_vs_rule_agreement"])
    fr = res["feature_relevance"]
    print("\nFeature relevance (random forest on all five features):")
    print("  permutation importance (macro-F1 drop):", fr["permutation_importance_macro_f1_drop"])
    print("  grouped Weight+Height+BMI permutation:", fr["grouped_numeric_permutation_macro_f1_drop"])
    print("  impurity importance:", fr["impurity_importance"])
    print("\nInput sweep (deployed model):", res["input_sweep_deployed_model"])
    print("\nNote: labels are synthetic and rule-generated; scores show the mapping is reproduced, not real-world accuracy.")
    print("Saved reports/evaluation_results.json")


if __name__ == "__main__":
    main()
