# AI Workout & Diet Recommendation System

An AI-powered fitness recommendation web application that generates personalized workout and diet plans based on user body metrics, fitness goals, and experience level using Machine Learning.

The application predicts the most suitable workout plan and provides a weekly workout schedule along with a personalized diet recommendation through a modern React-based user interface.

---

## Features

- AI-powered workout recommendation
- Personalized diet plan generation
- Weekly workout schedule
- Machine Learning-based prediction
- React + Vite frontend
- Tailwind CSS responsive UI
- REST API integration
- Input validation
- Loading indicator and error handling
- Modular component architecture

---

## Tech Stack

### Frontend

- React 19
- Vite
- Tailwind CSS v4
- JavaScript (ES6+)

### Backend

- Node.js
- Express.js

### Machine Learning

- Python
- Flask
- Scikit-learn
- Pickle

---

## Project Structure

```text
Workout-and-diet-recommendation-system/
│
├── frontend/
│   │
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   ├── ui/
│   │   │   └── features/
│   │   │       └── Workout/
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app.js
│   ├── package.json
│   └── node_modules/
│
├── ml-service/
│   ├── ml_api.py
│   ├── model.pkl
│   ├── le_goal.pkl
│   ├── le_exp.pkl
│   ├── le_plan.pkl
│   └── requirements.txt
│
└── README.md
```

---

## System Architecture

```text
React + Vite + Tailwind CSS
            │
            ▼
     Express.js Backend
            │
            ▼
        Flask API
            │
            ▼
 Machine Learning Model
            │
            ▼
Workout & Diet Recommendation
```

---

## Ports Used

| Service | Port |
|---------|------|
| React (Vite) | 5173 |
| Express Backend | 3000 |
| Flask ML API | 5001 |

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mosaqhibkhan/Workout-and-diet-recommendation-system.git

cd Workout-and-diet-recommendation-system
```

### 2. Install and Run the Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

### 3. Install and Run the Backend

```bash
cd backend

npm install

npm start
```

Backend runs at:

```
http://localhost:3000
```

---

### 4. Install and Run the ML Service

```bash
cd ml-service

pip install -r requirements.txt

python ml_api.py
```

ML service runs at:

```
http://localhost:5001
```

---

## Application Workflow

```text
User

↓

React Frontend

↓

Express Backend

↓

Flask Machine Learning API

↓

Scikit-Learn Prediction Model

↓

Workout Plan + Diet Plan

↓

Results Displayed to User
```

---

## Screenshots

Add screenshots of the application inside a `screenshots` folder.

Example:

```text
screenshots/
├── home.png
├── prediction.png
└── results.png
```

---

## Future Improvements

- User authentication
- Workout history
- Nutrition tracking
- BMI and body fat analysis
- Progress dashboard
- Exercise demonstration videos
- PDF export
- Mobile application
- Deployment with Docker
- Cloud database integration

---

## Author

**Mohammed Saqhib Uddin Khan**

GitHub:  
https://github.com/mosaqhibkhan

LinkedIn:  
https://www.linkedin.com/in/mohammed-saqhib-uddin-khan-66aa1a354

---

## License

This project is intended for educational and portfolio purposes.