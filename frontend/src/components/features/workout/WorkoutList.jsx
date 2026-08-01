const WorkoutList = ({ workout }) => {
  return (
    <>
      {Object.entries(workout).map(([day, exercise]) => {
        const isRest = exercise.toLowerCase().includes("rest");

        return (
          <div
            key={day}
            className="flex gap-5 border-b border-gray-800 px-6 py-4 last:border-none"
          >
            <div
              className={`w-16 font-bold uppercase ${
                isRest ? "text-gray-500" : "text-lime-300"
              }`}
            >
              {day.toUpperCase()}
            </div>

            <div className="text-gray-300">
              {exercise}
            </div>
          </div>
        );
      })}
    </>
  );
};

export default WorkoutList;