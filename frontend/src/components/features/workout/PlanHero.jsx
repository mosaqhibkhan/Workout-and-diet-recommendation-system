const PlanHero = ({ result }) => {
  const planName = result.plan.replaceAll("_", " ");

  return (
    <div className="relative mb-6 flex flex-col justify-between overflow-hidden rounded-2xl border border-gray-800 bg-[#16161f] p-8 md:flex-row md:items-center">
      <div className="absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r from-cyan-400 to-lime-300"></div>
      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.15em] text-gray-400">
          Your Recommended Plan
        </p>

        <h2 className="text-4xl font-bold">
          {planName}
        </h2>

        <p className="mt-3 text-green-400">
           {result.message}
        </p>
      </div>

      <div className="rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-6 py-4 text-3xl font-bold text-cyan-300">
        {planName}
      </div>
    </div>
  );
};

export default PlanHero;