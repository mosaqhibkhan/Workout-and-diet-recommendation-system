import { useEffect, useRef, useState } from "react";

import Results from "./Results";

import InputField from "../../ui/InputField";
import SelectField from "../../ui/SelectField";
import Button from "../../ui/Button";
import ErrorAlert from "../../ui/ErrorAlert";

import { getWorkoutPlan } from "../../../services/api";

const WorkoutForm = () => {
  // Form State
  const [weight, setWeight] = useState("");
  const [height, setHeight] = useState("");
  const [goal, setGoal] = useState("Cut");
  const [experience, setExperience] = useState("Beginner");

  // UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // API Response
  const [result, setResult] = useState(null);

  // Reference to Results Section
  const resultRef = useRef(null);

  // Scroll to results whenever a new result arrives
  useEffect(() => {
    if (result) {
      resultRef.current?.scrollIntoView({
        behavior: "smooth",
      });
    }
  }, [result]);

  const handleSubmit = async () => {
    setError("");

    const w = Number(weight);
    const h = Number(height);

    if (!w || !h) {
      setError("Please enter valid weight and height.");
      return;
    }

    if (w < 20 || w > 300) {
      setError("Weight must be between 20 and 300 kg.");
      return;
    }

    if (h < 100 || h > 250) {
      setError("Height must be between 100 and 250 cm.");
      return;
    }

    try {
      setLoading(true);

      const data = await getWorkoutPlan({
        weight: w,
        height: h,
        goal,
        experience,
      });

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <ErrorAlert message={error} />

      <div className="relative overflow-hidden rounded-2xl border border-gray-800 bg-[#16161f] p-10">

        {/* Top Gradient Line */}
        <div className="absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r from-lime-300 to-cyan-400"></div>

        <div className="mb-8 grid gap-6 md:grid-cols-2">
          <InputField
            label="Weight (kg)"
            type="number"
            placeholder="72"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
          />

          <InputField
            label="Height (cm)"
            type="number"
            placeholder="175"
            value={height}
            onChange={(e) => setHeight(e.target.value)}
          />

          <SelectField
            label="Goal"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            options={[
              { value: "Cut", label: "Cut – Lose Fat" },
              { value: "Bulk", label: "Bulk – Build Muscle" },
              { value: "Maintain", label: "Maintain – Stay Fit" },
            ]}
          />

          <SelectField
            label="Experience"
            value={experience}
            onChange={(e) => setExperience(e.target.value)}
            options={[
              { value: "Beginner", label: "Beginner" },
              { value: "Intermediate", label: "Intermediate" },
              { value: "Advanced", label: "Advanced" },
            ]}
          />
        </div>

        <Button loading={loading} onClick={handleSubmit}>
          Generate My Plan
        </Button>
      </div>

      {/* Results Section */}
      <div ref={resultRef}>
        <Results result={result} />
      </div>
    </>
  );
};

export default WorkoutForm;