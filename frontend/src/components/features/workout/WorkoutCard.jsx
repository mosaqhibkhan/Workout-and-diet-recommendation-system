import WorkoutList from "./WorkoutList";

const WorkoutCard = ({ workout }) => {
  return (
    <div className="overflow-hidden rounded-2xl border border-gray-800 bg-[#16161f] shadow-lg">
      <div className="border-b border-gray-800 p-6">
        <h2 className="text-2xl font-bold">
           Weekly Workout Schedule
        </h2>
      </div>

      <WorkoutList workout={workout} />
    </div>
  );
};

export default WorkoutCard;