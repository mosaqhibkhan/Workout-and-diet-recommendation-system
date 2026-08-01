const DietList = ({ diet }) => {
  return (
    <>
      {Object.entries(diet).map(([key, value]) => (
        <div
          key={key}
          className="border-b border-gray-800 px-6 py-4 last:border-none"
        >
          <div className="mb-1 text-xs font-bold uppercase tracking-widest text-cyan-400">
            {key}
          </div>

          <div className="text-gray-300">
            {value}
          </div>
        </div>
      ))}
    </>
  );
};

export default DietList;