import pickle
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load ML model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("le_goal.pkl", "rb") as f:
    le_goal = pickle.load(f)

with open("le_exp.pkl", "rb") as f:
    le_exp = pickle.load(f)

with open("le_plan.pkl", "rb") as f:
    le_plan = pickle.load(f)

@app.route("/ml-predict", methods=["POST"])
def predict():

    data = request.json

    weight = float(data["weight"])
    height = float(data["height"])
    goal = data["goal"]
    experience = data["experience"]

    goal_enc = le_goal.transform([goal])[0]
    exp_enc = le_exp.transform([experience])[0]

    height_m = height / 100
    bmi = round(weight / (height_m ** 2), 2)

    features = pd.DataFrame(
        [[weight, height, bmi, goal_enc, exp_enc]],
        columns=["Weight", "Height", "BMI", "Goal", "Experience"]
    )

    prediction = model.predict(features)[0]

    plan_name = le_plan.inverse_transform([prediction])[0]

    return jsonify({
        "plan": plan_name
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })

if __name__ == "__main__":
    app.run(port=5001)