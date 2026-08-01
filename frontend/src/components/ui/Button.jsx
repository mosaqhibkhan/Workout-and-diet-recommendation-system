import Spinner from "./Spinner";

const Button = ({ children, loading, onClick }) => {
  return (
    <button
      disabled={loading}
      onClick={onClick}
      className={`w-full rounded-xl py-4 text-lg font-bold uppercase tracking-[0.15em] transition duration-300

${
loading
?

"cursor-not-allowed bg-gray-700 text-gray-400"

:

"bg-lime-300 text-black shadow-lg shadow-lime-300/20 hover:-translate-y-1 hover:bg-lime-200"

}`}
    >
      {loading ? <Spinner /> : children}
    </button>
  );
};

export default Button;

