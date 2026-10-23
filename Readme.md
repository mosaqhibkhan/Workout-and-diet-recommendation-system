# Workout & Diet Recommendation System

A full-stack web application that generates 7-day workout schedules and goal-based diet plans according to a user's weight, height, fitness goal, and experience level.

Users can choose between **Cut, Bulk, and Maintain** and receive a structured workout plan alongside a diet template with calorie targets, macronutrient ratios, meal suggestions, and foods to limit.

## Features

* **Workout Recommendations:** Selects from nine workout plans based on fitness goal and experience level.
* **Diet Recommendations:** Provides predefined diet templates for cutting, bulking, and maintaining weight.
* **Machine Learning Integration:** Uses a trained Scikit-learn classification model to select workout plans.
* **Full-Stack Architecture:** Integrates a React frontend, Express backend, and Flask ML service.
* **Input Validation:** Validates user inputs before processing recommendations.
* **Automated Testing:** Includes tests for the backend API, ML service, and frontend build.

## Tech Stack

| Component        | Technologies                        |
| ---------------- | ----------------------------------- |
| Frontend         | React, Vite, Tailwind CSS           |
| Backend          | Node.js, Express.js                 |
| Machine Learning | Python, Scikit-learn, Pandas, NumPy |
| ML API           | Flask                               |
| Testing          | Pytest, Node.js Test Runner         |

## Machine Learning Implementation

The application uses a machine learning pipeline built with Python and Scikit-learn to classify user inputs into one of nine workout plan categories.

### 1. Dataset Generation

A Python script generates a synthetic dataset containing fitness goals, experience levels, numerical attributes, and corresponding workout plan labels.

The dataset is used to train and evaluate candidate classification models.

### 2. Feature Selection

The model uses two input features:

* **Goal:** Cut, Bulk, or Maintain.
* **Experience:** Beginner, Intermediate, or Advanced.

These features determine the appropriate workout plan category.

### 3. Model Training

The training pipeline compares candidate classification models using stratified data splitting and 5-fold cross-validation.

The selected model is trained on the training dataset and evaluated against a held-out test dataset. The trained pipeline is then serialized and saved for future predictions.

### 4. Prediction

During application use, the Flask service loads the saved model and processes incoming prediction requests.

The model returns one of nine possible workout plan labels:

| Fitness Goal | Beginner             | Intermediate             | Advanced             |
| ------------ | -------------------- | ------------------------ | -------------------- |
| Cut          | FatLoss_Beginner     | FatLoss_Intermediate     | FatLoss_Advanced     |
| Bulk         | MuscleGain_Beginner  | MuscleGain_Intermediate  | MuscleGain_Advanced  |
| Maintain     | Maintenance_Beginner | Maintenance_Intermediate | Maintenance_Advanced |

### 5. Diet Recommendation Logic

Diet recommendations use a rule-based approach implemented in the Express backend.

Each fitness goal maps to a predefined diet template containing calorie targets, macronutrient ratios, meal suggestions, and foods to limit.

**Machine learning selects the workout plan, while the backend determines the diet template based on the selected fitness goal.**

## Application Architecture

The application consists of three services.

| Service          | Responsibility                                                                         |
| ---------------- | -------------------------------------------------------------------------------------- |
| React Frontend   | Collects user inputs and displays workout and diet recommendations.                    |
| Express Backend  | Validates inputs, communicates with the ML service, and assembles the recommendations. |
| Flask ML Service | Loads the trained Scikit-learn pipeline and predicts the workout plan category.        |

### Request Flow

1. The user enters their details through the React interface.
2. The frontend sends the request to the Express backend.
3. Express validates the input and forwards the relevant features to Flask.
4. Flask runs the trained model and returns the predicted workout plan label.
5. Express maps the label to the corresponding 7-day workout template.
6. Express selects the diet template based on the fitness goal.
7. The combined recommendations are returned to the frontend.

## Project Structure

```text
Workout-and-diet-recommendation-system/
│
├── frontend/
│   └── src/
│       └── services/
│           └── api.js
│
├── backend/
│   ├── app.js
│   └── test/
│
└── ml-service/
    ├── ml_api.py
    ├── workout_ml.py
    ├── generate_synthetic_data.py
    ├── train_model.py
    ├── evaluate_model.py
    ├── data/
    ├── artifacts/
    ├── reports/
    └── tests/
```

## Prerequisites

Ensure the following are installed:

* Python 3.11 or later
* Node.js 22.9 or later
* npm

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/mosaqhibkhan/Workout-and-diet-recommendation-system.git

cd Workout-and-diet-recommendation-system
```

### 2. Set Up the ML Service

Navigate to the ML service directory and create a virtual environment.

```bash
cd ml-service

python -m venv .venv
```

Activate the environment.

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### 3. Set Up the Backend

Open a new terminal at the project root.

```bash
cd backend
npm install
```

### 4. Set Up the Frontend

Open another terminal at the project root.

```bash
cd frontend
npm install
```

The trained model is included in the repository, so retraining is not required to run the application.

## Running the Application

Start each service in a separate terminal.

### Terminal 1: ML Service

```bash
cd ml-service
python ml_api.py
```

Service address: `http://127.0.0.1:5001`

### Terminal 2: Backend

```bash
cd backend
npm start
```

Service address: `http://127.0.0.1:3000`

### Terminal 3: Frontend

```bash
cd frontend
npm run dev
```

Open the application in your browser:

**http://localhost:5173**

## Training the ML Model

To regenerate the dataset, train the model, and evaluate its performance, execute the following commands from the `ml-service` directory.

### Generate the Dataset

```bash
python generate_synthetic_data.py
```

Generates the synthetic workout dataset.

### Train the Model

```bash
python train_model.py
```

Compares candidate models, selects the preferred model, and saves the trained pipeline.

### Evaluate the Model

```bash
python evaluate_model.py
```

Evaluates the trained model and generates evaluation reports.

These steps are optional when using the existing trained model included in the repository.

## Testing

The project includes tests for the ML service and backend, along with frontend linting and production-build checks.

### ML Service

```bash
cd ml-service

pip install -r requirements-dev.txt

python -m pytest -q
```

### Backend

```bash
cd backend

npm test
```

### Frontend

```bash
cd frontend

npm run lint

npm run build
```

## Future Enhancements

* User authentication and profile management.
* Workout progress and fitness tracking.
* More flexible workout and nutrition recommendations.
* Additional workout variations and fitness goals.

## Author

**Mohammed Saqhib Uddin Khan**

* **GitHub:** [mosaqhibkhan](https://github.com/mosaqhibkhan)
* **LinkedIn:** [Mohammed Saqhib Uddin Khan](https://www.linkedin.com/in/mohammed-saqhib-uddin-khan-66aa1a354)
