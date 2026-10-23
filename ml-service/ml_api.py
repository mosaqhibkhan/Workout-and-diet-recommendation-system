import math
import os
from pathlib import Path

import joblib
from flask import Flask, request, jsonify

from workout_ml import (
    EXPERIENCES, FEATURES, GOALS, HEIGHT_RANGE_CM, MODEL_PATH, PLANS, WEIGHT_RANGE_KG, build_features,
)


def load_model(path):
    """Load the trained pipeline produced by train_model.py (never trained here)."""
    model = joblib.load(path)
    expected = list(getattr(model, "feature_names_in_", []))
    if expected != FEATURES:
        raise ValueError(f"Model was trained on features {expected}, but the service sends {FEATURES}")
    unknown = set(map(str, model.classes_)) - set(PLANS)
    if unknown:
        raise ValueError(f"Model predicts unknown plans: {sorted(unknown)}")
    return model


def parse_number(data, field, lo, hi):
    value = data[field]
    if isinstance(value, bool):
        raise ValueError(f"'{field}' must be a number.")
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"'{field}' must be a number.")
    if not math.isfinite(value) or not lo <= value <= hi:
        raise ValueError(f"'{field}' must be between {lo:g} and {hi:g}.")
    return value


def create_app(model_path=None):
    # Only the Express backend calls this service, so CORS is not enabled.
    app = Flask(__name__)

    model_path = Path(model_path or os.environ.get("MODEL_PATH", MODEL_PATH))
    try:
        model = load_model(model_path)
    except Exception as exc:  # keep the service up so /health can report the problem
        model = None
        app.logger.error("Could not load model from %s: %s: %s", model_path, type(exc).__name__, exc)

    @app.route("/ml-predict", methods=["POST"])
    def predict():

        if model is None:
            return jsonify({"error": "Model not loaded."}), 503

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400

        for field in ["weight", "height", "goal", "experience"]:
            if field not in data:
                return jsonify({"error": f"Missing field: '{field}'"}), 400

        try:
            weight = parse_number(data, "weight", *WEIGHT_RANGE_KG)
            height = parse_number(data, "height", *HEIGHT_RANGE_CM)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        goal = str(data["goal"]).strip()
        experience = str(data["experience"]).strip()

        if goal not in GOALS:
            return jsonify({"error": f"Invalid goal '{goal}'. Choose: {', '.join(GOALS)}"}), 400

        if experience not in EXPERIENCES:
            return jsonify({"error": f"Invalid experience '{experience}'. Choose: {', '.join(EXPERIENCES)}"}), 400

        features = build_features(weight, height, goal, experience)

        plan_name = str(model.predict(features)[0])

        return jsonify({
            "plan": plan_name
        })

    @app.route("/health")
    def health():
        if model is None:
            return jsonify({"status": "error", "error": "Model not loaded."}), 503
        return jsonify({
            "status": "ok"
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5001)))
