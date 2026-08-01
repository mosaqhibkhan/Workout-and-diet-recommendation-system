import PlanHero from "./PlanHero";
import WorkoutCard from "./WorkoutCard";
import DietCard from "./DietCard";

const Results = ({ result }) => {
  if (!result) return null;

  return (
    <section className="mt-8 animate-[fadeIn_.6s_ease]">
      <PlanHero result={result} />

      <div className="grid gap-6 lg:grid-cols-2">
        <WorkoutCard workout={result.workout} />

        <DietCard diet={result.diet} />
      </div>
    </section>
  );
};

export default Results;