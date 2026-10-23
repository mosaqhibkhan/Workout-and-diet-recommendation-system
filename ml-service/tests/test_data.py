import pandas as pd
import pytest

from generate_synthetic_data import generate
from workout_ml import (
    DATA_PATH, PLANS, DataValidationError, data_quality_summary, load_dataset, split_dataset, validate_dataset,
)


@pytest.fixture
def df():
    return pd.read_csv(DATA_PATH)


def test_committed_dataset_is_reproducible_from_generator(df):
    pd.testing.assert_frame_equal(df, generate(), check_dtype=False)


def test_committed_dataset_passes_validation(df):
    validate_dataset(df)


@pytest.mark.parametrize("mutate, message", [
    (lambda d: d.drop(columns="BMI"), "Missing columns"),
    (lambda d: d.assign(Weight=d["Weight"].where(d.index != 0)), "Missing values"),
    (lambda d: d.assign(Height=d["Height"].astype(str)), "not numeric"),
    (lambda d: d.assign(Goal=d["Goal"].replace("Cut", "Shred")), "Unknown values in 'Goal'"),
    (lambda d: d.assign(Experience=d["Experience"].replace("Beginner", "Pro")), "Unknown values in 'Experience'"),
    (lambda d: d.assign(Plan=d["Plan"].replace("FatLoss_Beginner", "Yoga")), "Unknown values in 'Plan'"),
    (lambda d: d.assign(Weight=d["Weight"] * 10), "Weight outside"),
    (lambda d: d.assign(Height=d["Height"] / 10), "Height outside"),
    (lambda d: d.assign(BMI=d["BMI"] + 1), "BMI inconsistent"),
])
def test_validation_rejects_invalid_data(df, mutate, message):
    with pytest.raises(DataValidationError, match=message):
        validate_dataset(mutate(df))


def test_quality_summary_reports_duplicates_and_conflicts(df):
    first = df.iloc[[0]]
    conflict = first.assign(Plan=next(p for p in PLANS if p != first["Plan"].iloc[0]))
    summary = data_quality_summary(pd.concat([df, first, conflict], ignore_index=True))
    assert summary["n_exact_duplicate_rows"] == data_quality_summary(df)["n_exact_duplicate_rows"] + 1
    assert summary["n_feature_vectors_with_conflicting_labels"] >= 1
    assert set(summary["class_counts"]) == set(PLANS)


def test_load_dataset_drops_duplicates():
    assert not load_dataset().duplicated().any()


def test_split_is_reproducible_stratified_and_disjoint():
    df = load_dataset()
    X_tr1, X_te1, y_tr1, _ = split_dataset(df)
    _, X_te2, _, _ = split_dataset(df)
    assert list(X_te1.index) == list(X_te2.index)
    assert set(X_tr1.index).isdisjoint(X_te1.index)
    assert set(y_tr1) == set(PLANS)
