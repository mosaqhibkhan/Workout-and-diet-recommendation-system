import Header from "./components/layout/Header";
import WorkoutForm from "./components/features/Workout/WorkoutForm";

function App() {
  return (
    <div className="relative min-h-screen overflow-x-hidden bg-[#0a0a0f] text-white">

      {/* Background Glow */}
      <div className="pointer-events-none fixed inset-0 -z-10">

        <div className="absolute right-0 top-0 h-[500px] w-[500px] rounded-full bg-lime-300/5 blur-3xl"></div>

        <div className="absolute bottom-0 left-0 h-[500px] w-[500px] rounded-full bg-cyan-400/5 blur-3xl"></div>

      </div>

      <div className="mx-auto max-w-5xl px-6 py-12">

        <Header />

        <WorkoutForm />

      </div>

    </div>
  );
}

export default App;