const Header = () => {
  return (
    <header className="mb-14 text-center">

      <div className="mb-6 inline-flex rounded-full border border-lime-300/20 bg-lime-300/10 px-5 py-2 text-xs font-semibold uppercase tracking-[0.15em] text-lime-300">

        Workout &amp; Diet Planner

      </div>

      <h1 className="mb-4 text-6xl font-black uppercase leading-none tracking-wider sm:text-8xl">

        Your Weekly

        <br />

        <span className="text-lime-300">
          Workout
        </span>

        {" "}Plan

      </h1>

      <p className="mx-auto max-w-md text-gray-400 leading-7">

        Choose your goal and experience level to get a weekly workout schedule and a matching diet template.

      </p>

    </header>
  );
};

export default Header;