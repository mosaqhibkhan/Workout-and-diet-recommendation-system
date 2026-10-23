import joblib
import pytest

from evaluate_model import input_grid
from ml_api import create_app
from workout_ml import EXPERIENCES, GOALS, MODEL_PATH, rule_based_plan

VALID = {"weight": 72, "height": 175, "goal": "Cut", "experience": "Beginner"}


@pytest.fixture(scope="module")
def client():
    return create_app().test_client()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200 and res.get_json() == {"status": "ok"}


@pytest.mark.parametrize("goal", GOALS)
@pytest.mark.parametrize("experience", EXPERIENCES)
def test_all_goal_experience_combinations(client, goal, experience):
    res = client.post("/ml-predict", json={**VALID, "goal": goal, "experience": experience})
    assert res.status_code == 200
    assert res.get_json() == {"plan": rule_based_plan(goal, experience)}


def test_numeric_strings_still_accepted(client):
    res = client.post("/ml-predict", json={**VALID, "weight": "72", "height": "175.5"})
    assert res.status_code == 200 and res.get_json()["plan"] == "FatLoss_Beginner"


@pytest.mark.parametrize("field", ["weight", "height", "goal", "experience"])
def test_missing_field(client, field):
    body = {k: v for k, v in VALID.items() if k != field}
    res = client.post("/ml-predict", json=body)
    assert res.status_code == 400 and field in res.get_json()["error"]


@pytest.mark.parametrize("override", [{"goal": "Shred"}, {"experience": "Pro"}, {"goal": None}])
def test_invalid_category(client, override):
    res = client.post("/ml-predict", json={**VALID, **override})
    assert res.status_code == 400 and "Invalid" in res.get_json()["error"]


@pytest.mark.parametrize("override", [
    {"weight": "abc"}, {"weight": None}, {"weight": True}, {"height": [175]},
    {"weight": 19.9}, {"weight": 301}, {"height": 99}, {"height": 251},
])
def test_invalid_numeric(client, override):
    res = client.post("/ml-predict", json={**VALID, **override})
    assert res.status_code == 400 and "error" in res.get_json()


@pytest.mark.parametrize("raw", [
    '{"weight": NaN, "height": 175, "goal": "Cut", "experience": "Beginner"}',
    '{"weight": 72, "height": Infinity, "goal": "Cut", "experience": "Beginner"}',
])
def test_nan_and_infinity_rejected(client, raw):
    res = client.post("/ml-predict", data=raw, content_type="application/json")
    assert res.status_code == 400


@pytest.mark.parametrize("kwargs", [
    {"data": "not json", "content_type": "application/json"},
    {"json": [1, 2, 3]},
    {"data": "weight=72", "content_type": "application/x-www-form-urlencoded"},
])
def test_non_object_body(client, kwargs):
    assert client.post("/ml-predict", **kwargs).status_code == 400


def test_missing_model_file_is_controlled(tmp_path):
    _assert_model_unavailable(create_app(tmp_path / "missing.joblib").test_client())


def test_corrupt_model_file_is_controlled(tmp_path):
    path = tmp_path / "corrupt.joblib"
    path.write_bytes(b"not a model")
    _assert_model_unavailable(create_app(path).test_client())


def test_model_with_wrong_feature_schema_is_rejected(tmp_path):
    from workout_ml import load_dataset, make_decision_tree, split_dataset
    X_train, _, y_train, _ = split_dataset(load_dataset())
    wrong = make_decision_tree(numeric=[]).fit(X_train[["Goal", "Experience"]], y_train)
    path = tmp_path / "wrong_schema.joblib"
    joblib.dump(wrong, path)
    _assert_model_unavailable(create_app(path).test_client())


def _assert_model_unavailable(client):
    assert client.get("/health").status_code == 503
    res = client.post("/ml-predict", json=VALID)
    assert res.status_code == 503 and res.get_json() == {"error": "Model not loaded."}


def test_served_model_matches_rule_over_input_range():
    grid = input_grid(step=10.0)
    expected = [rule_based_plan(g, e) for g, e in zip(grid["Goal"], grid["Experience"])]
    assert list(joblib.load(MODEL_PATH).predict(grid)) == expected


def test_cors_not_enabled(client):
    res = client.post("/ml-predict", json=VALID, headers={"Origin": "http://evil.example"})
    assert "Access-Control-Allow-Origin" not in res.headers


def test_no_training_endpoints_exposed():
    rules = {r.rule for r in create_app().url_map.iter_rules()}
    assert rules == {"/ml-predict", "/health", "/static/<path:filename>"}
