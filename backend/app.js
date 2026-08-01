const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();

app.use(cors());
app.use(express.json());

/* ─── Workout Plans ───────────────────────────────────────────────────────── */

const WORKOUT_PLANS = {
  "FatLoss_Beginner": {
    "Day 1": "Brisk Walking (30 min), Bodyweight Squats (3×15), Push-Ups (3×10)",
    "Day 2": "Cycling (20 min), Dumbbell Rows (3×12), Plank (3×30 sec)",
    "Day 3": "Rest / Light Stretching",
    "Day 4": "Jump Rope (15 min), Lunges (3×12), Dumbbell Shoulder Press (3×10)",
    "Day 5": "Jogging (25 min), Glute Bridges (3×15), Tricep Dips (3×10)",
    "Day 6": "Swimming or Aerobics (30 min), Core Circuit (3 rounds)",
    "Day 7": "Full Rest"
  },

  "FatLoss_Intermediate": {
    "Day 1": "Burpees (4×10), Bench Press (4×10), Goblet Squats (4×12)",
    "Day 2": "Running (30 min), Deadlift (3×8), Plank Variations (3×45 sec)",
    "Day 3": "HIIT Circuit (20 min), Pull-Ups (3×8), Mountain Climbers (3×20)",
    "Day 4": "Active Recovery – Yoga or Stretching",
    "Day 5": "Kettlebell Swings (4×15), Overhead Press (4×10), Romanian Deadlift (4×10)",
    "Day 6": "Cardio Intervals (25 min), Core Superset (4 rounds)",
    "Day 7": "Full Rest"
  },

  "FatLoss_Advanced": {
    "Day 1": "Barbell Complex (5×5), Box Jumps (4×10), Battle Ropes (3×30 sec)",
    "Day 2": "Sprint Intervals (30 min), Weighted Pull-Ups (4×6), Hanging Leg Raises (4×12)",
    "Day 3": "Olympic Lifting – Power Cleans (5×3), Front Squats (5×5)",
    "Day 4": "Active Recovery – Mobility Work",
    "Day 5": "Deadlift (5×5), Weighted Dips (4×8), TRX Core (4 rounds)",
    "Day 6": "CrossFit-style WOD (40 min), Loaded Carries",
    "Day 7": "Full Rest"
  },

  "MuscleGain_Beginner": {
    "Day 1": "Bench Press (3×10), Dumbbell Flyes (3×12), Push-Ups (3×15)",
    "Day 2": "Squat (3×10), Leg Press (3×12), Calf Raises (3×15)",
    "Day 3": "Rest",
    "Day 4": "Dumbbell Rows (3×10), Lat Pulldown (3×12), Bicep Curls (3×12)",
    "Day 5": "Overhead Press (3×10), Lateral Raises (3×12), Tricep Pushdown (3×12)",
    "Day 6": "Full Body Light Circuit, Core Work",
    "Day 7": "Full Rest"
  },

  "MuscleGain_Intermediate": {
    "Day 1": "Bench Press (4×8), Incline DB Press (4×10), Cable Flyes (3×12)",
    "Day 2": "Squat (4×8), Romanian Deadlift (3×10), Leg Curls (3×12)",
    "Day 3": "Pull-Ups (4×8), Barbell Row (4×8), Face Pulls (3×15)",
    "Day 4": "Rest / Mobility",
    "Day 5": "Overhead Press (4×8), Arnold Press (3×10), Lateral Raises (4×12)",
    "Day 6": "Deadlift (4×6), Farmer Walks, Core Circuit",
    "Day 7": "Full Rest"
  },

  "MuscleGain_Advanced": {
    "Day 1": "Heavy Bench Press (5×5), Weighted Dips (4×6), DB Flyes Drop Set",
    "Day 2": "Squat (5×5), Hack Squat (4×8), Bulgarian Split Squat (3×10)",
    "Day 3": "Weighted Pull-Ups (5×5), Pendlay Row (4×6), Straight-Arm Pulldown (3×15)",
    "Day 4": "Active Recovery – Foam Rolling, Stretching",
    "Day 5": "Overhead Press (5×5), Behind-Neck Press (3×8), Upright Rows (4×10)",
    "Day 6": "Deadlift (5×3), Rack Pulls, Strongman Accessories",
    "Day 7": "Full Rest"
  },

  "Maintenance_Beginner": {
    "Day 1": "Jogging (20 min), Bodyweight Squats (3×12), Push-Ups (3×10)",
    "Day 2": "Cycling (25 min), Dumbbell Rows (3×10), Plank (3×30 sec)",
    "Day 3": "Rest / Yoga",
    "Day 4": "Swimming (20 min), Lunges (3×10), Core Work",
    "Day 5": "Brisk Walk (30 min), Light Resistance Bands Circuit",
    "Day 6": "Recreational Sport or Dance (30 min)",
    "Day 7": "Full Rest"
  },

  "Maintenance_Intermediate": {
    "Day 1": "Running (30 min), Compound Lift – Squat or Bench (3×10)",
    "Day 2": "Full Body Resistance Training (moderate intensity)",
    "Day 3": "Yoga / Stretching / Mobility",
    "Day 4": "HIIT (20 min), Core Superset",
    "Day 5": "Cycling or Swimming (30 min), Upper Body Maintenance",
    "Day 6": "Recreational Activity or Sports",
    "Day 7": "Full Rest"
  },

  "Maintenance_Advanced": {
    "Day 1": "Strength Training – Push (5×5 moderate weight)",
    "Day 2": "Strength Training – Pull (5×5 moderate weight)",
    "Day 3": "Cardio + Mobility (40 min combined)",
    "Day 4": "Legs – Squat + Accessories (4×8)",
    "Day 5": "Functional Training – Olympic Lifts or Kettlebells",
    "Day 6": "Active Recovery – Sport or Long Walk",
    "Day 7": "Full Rest"
  }
};

/* ─── Diet Plans ─────────────────────────────────────────────────────────── */

const DIET_PLANS = {
  "Cut": {
    "Goal": "Calorie Deficit – Fat Loss",
    "Calories": "~1,800–2,100 kcal/day (adjust by body weight)",
    "Macros": "Protein: 40% | Carbs: 35% | Fats: 25%",
    "Breakfast": "Egg white omelette with spinach + black coffee",
    "Mid-Morning": "Greek yogurt (low fat) + a handful of almonds",
    "Lunch": "Grilled chicken breast + steamed broccoli + brown rice (small portion)",
    "Evening Snack": "Whey protein shake + apple",
    "Dinner": "Baked salmon + roasted vegetables + quinoa",
    "Hydration": "3–4 litres of water daily",
    "Avoid": "Processed sugar, fried foods, alcohol, white bread"
  },

  "Bulk": {
    "Goal": "Calorie Surplus – Muscle Gain",
    "Calories": "~3,000–3,500 kcal/day (adjust by body weight)",
    "Macros": "Protein: 30% | Carbs: 50% | Fats: 20%",
    "Breakfast": "5 whole eggs + oats with banana + whole milk",
    "Mid-Morning": "Peanut butter toast + protein shake",
    "Lunch": "Rice + dal + paneer/chicken + vegetables",
    "Evening Snack": "Mass gainer shake + mixed nuts",
    "Dinner": "Pasta with ground beef/tofu + salad + bread",
    "Hydration": "3–4 litres of water daily",
    "Avoid": "Junk food, empty-calorie snacks"
  },

  "Maintain": {
    "Goal": "Balanced Nutrition – Weight Maintenance",
    "Calories": "~2,200–2,600 kcal/day (adjust by body weight)",
    "Macros": "Protein: 30% | Carbs: 45% | Fats: 25%",
    "Breakfast": "Whole grain cereal + milk + fruit",
    "Mid-Morning": "Mixed nuts + green tea",
    "Lunch": "Grilled protein (chicken/fish/tofu) + vegetables + rice or roti",
    "Evening Snack": "Protein bar or boiled eggs",
    "Dinner": "Lean meat or lentils + salad + whole grain bread",
    "Hydration": "2.5–3.5 litres of water daily",
    "Avoid": "Overeating, skipping meals, excess sugar"
  }
};

const VALID_GOALS = ["Cut", "Bulk", "Maintain"];
const VALID_EXP = ["Beginner", "Intermediate", "Advanced"];

/* ─── API Endpoint ───────────────────────────────────────────────────────── */

app.post("/predict", async (req, res) => {

  try {

    const data = req.body;

    if (!data) {
      return res.status(400).json({
        error: "Invalid JSON body."
      });
    }

    const required = ["weight", "height", "goal", "experience"];

    for (const field of required) {
      if (!(field in data)) {
        return res.status(400).json({
          error: `Missing field: '${field}'`
        });
      }
    }

    const goal =
      String(data.goal).trim();

    const experience =
      String(data.experience).trim();

    if (!VALID_GOALS.includes(goal)) {
      return res.status(400).json({
        error: `Invalid goal '${goal}'. Choose: Cut, Bulk, Maintain`
      });
    }

    if (!VALID_EXP.includes(experience)) {
      return res.status(400).json({
        error: `Invalid experience '${experience}'. Choose: Beginner, Intermediate, Advanced`
      });
    }

    const weight = Number(data.weight);
    const height = Number(data.height);

    if (isNaN(weight) || isNaN(height)) {
      return res.status(400).json({
        error: "Weight and height must be numbers."
      });
    }

    if (weight < 20 || weight > 300) {
      return res.status(400).json({
        error: "Weight must be between 20 and 300 kg."
      });
    }

    if (height < 100 || height > 250) {
      return res.status(400).json({
        error: "Height must be between 100 and 250 cm."
      });
    }

    /* ─── Call Python ML API ───────────────── */

    const response = await axios.post(
      "http://127.0.0.1:5001/ml-predict",
      {
        weight,
        height,
        goal,
        experience
      }
    );

    const plan_name = response.data.plan;

    const workout =
      WORKOUT_PLANS[plan_name] ||
      { Error: "Plan not found in dictionary." };

    const diet =
      DIET_PLANS[goal] || {};

    return res.json({
      plan: plan_name,
      workout,
      diet,
      message:
        "Follow this plan consistently for 4 weeks for best results!"
    });

  } catch (error) {

    console.error(error.message);

    return res.status(500).json({
      error: "Prediction failed"
    });
  }
});

/* ─── Health Route ───────────────────────────────────────────────────────── */

app.get("/health", (req, res) => {
  res.json({
    status: "ok"
  });
});

/* ─── Start Server ───────────────────────────────────────────────────────── */

const PORT = 3000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});