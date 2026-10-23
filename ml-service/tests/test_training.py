import json

import joblib
import numpy as np
import pytest
from sklearn.inspection import permutation_importance

from evaluate_model import evaluate
from generate_synthetic_data import generate
from train_model import train
from workout_ml import (
    EXPERIENCES, FEATURES, GOALS, PLANS, RANDOM_SEED, RuleBasedClassifier, load_dataset, make_random_forest,
    rule_based_plan, split_dataset,
)


@pytest.fixture(scope="module")
def trained(tmp_path_factory):
    out = tmp_path_factory.mktemp("artifacts")
    model, meta = train(model_path=out / "m.joblib", metadata_path=out / "meta.json")
    return out, model, meta


@pytest.fixture(scope="module")
def X_test():
    return split_dataset(load_dataset())[1]


def test_training_is_reproducible(tmp_path, trained, X_test):
    _, first, _ = trained
    second, _ = train(model_path=tmp_path / "m.joblib", metadata_path=tmp_path / "meta.json")
    np.testing.assert_array_equal(first.predict_proba(X_test), second.predict_proba(X_test))


def test_model_serialization_round_trip(trained, X_test):
    out, model, _ = trained
    reloaded = joblib.load(out / "m.joblib")
    np.testing.assert_array_equal(model.predict_proba(X_test), reloaded.predict_proba(X_test))
    assert list(reloaded.classes_) == PLANS


def test_metadata_records_provenance(trained):
    out, _, meta = trained
    assert json.loads((out / "meta.json").read_text()) == meta
    assert meta["dataset"]["type"].startswith("SYNTHETIC")
    assert len(meta["dataset"]["sha256"]) == 64
    assert meta["random_seed"] == RANDOM_SEED


def test_rule_baseline_covers_all_combinations():
    assert {rule_based_plan(g, e) for g in GOALS for e in EXPERIENCES} == set(PLANS)
    assert rule_based_plan("Cut", "Beginner") == "FatLoss_Beginner"
    assert rule_based_plan("Bulk", "Advanced") == "MuscleGain_Advanced"
    assert rule_based_plan("Maintain", "Intermediate") == "Maintenance_Intermediate"


def test_rule_classifier_is_sklearn_compatible():
    X_tr, X_te, y_tr, y_te = split_dataset(load_dataset())
    assert RuleBasedClassifier().fit(X_tr, y_tr).score(X_te, y_te) == 1.0


@pytest.fixture(scope="module")
def results(trained, tmp_path_factory):
    out, _, _ = trained
    report_dir = tmp_path_factory.mktemp("reports")
    res = evaluate(model_path=out / "m.joblib", metadata_path=out / "meta.json", out_dir=report_dir, grid_step=10.0)
    assert json.loads((report_dir / "evaluation_results.json").read_text()) == res
    return res


def test_model_selection_picks_simplest_tied_learned_model(trained):
    _, model, meta = trained
    cv = meta["cross_validation"]
    assert {"dummy_most_frequent", "dummy_stratified", "rule_lookup"} <= set(cv)
    assert all(cv[n]["type"] == "baseline" for n in ["dummy_most_frequent", "dummy_stratified", "rule_lookup"])
    # Every learned model that sees Goal and Experience ties with the rule, so the simplest one wins.
    assert meta["selected_model"] == "decision_tree_goal_experience"
    assert meta["features_used_by_model"] == [f"cat__Goal_{g}" for g in GOALS] + [f"cat__Experience_{e}" for e in EXPERIENCES]
    assert model.named_steps["model"].get_n_leaves() == len(PLANS)


def test_evaluation_output_structure(results):
    assert {"label_audit", "model_selection", "deployed_model", "holdout_test",
            "feature_relevance", "input_sweep_deployed_model"} <= set(results)
    assert results["holdout_test"]["deployed_confusion_matrix"]["labels"] == PLANS
    assert set(results["holdout_test"]["deployed_per_class"]) == set(PLANS)
    assert results["deployed_model"]["estimator"] == "DecisionTreeClassifier"


def test_baseline_comparison(results):
    ho = results["holdout_test"]
    assert ho["deployed_vs_rule_agreement"] == 1.0
    assert ho["deployed_model"]["macro_f1"] >= ho["rule_baseline"]["macro_f1"]
    assert ho["dummy_stratified"]["macro_f1"] < 0.3


def test_feature_ablation_and_relevance(results):
    cv = results["model_selection"]["cross_validation_on_train_split"]
    assert cv["random_forest_goal_experience"]["cv_macro_f1_mean"] >= cv["random_forest_all_features"]["cv_macro_f1_mean"]
    assert cv["random_forest_numeric_only"]["cv_macro_f1_mean"] < 0.3
    fr = results["feature_relevance"]
    assert all(fr["permutation_importance_macro_f1_drop"][f]["mean"] == 0 for f in ["Weight", "Height", "BMI"])
    assert fr["grouped_numeric_permutation_macro_f1_drop"]["mean"] == 0
    assert results["input_sweep_deployed_model"]["predictions_differing_from_rule"] == 0


def test_permutation_importance_detects_a_relevant_numeric_feature():
    """Positive control: the method must flag BMI when the label really depends on it."""
    X = generate(600)[FEATURES]
    y = np.where(X["BMI"] >= 25, "High", "Low")
    model = make_random_forest().fit(X.iloc[:400], y[:400])
    perm = permutation_importance(model, X.iloc[400:], y[400:], n_repeats=10, random_state=RANDOM_SEED)
    imp = dict(zip(FEATURES, perm.importances_mean))
    assert imp["BMI"] > 0.1
    assert imp["Goal"] < 0.02 and imp["Experience"] < 0.02
