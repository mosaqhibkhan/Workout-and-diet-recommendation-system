const ErrorAlert = ({ message }) => {
  if (!message) return null;

  return (
    <div className="mb-6 rounded-lg border border-red-500/40 bg-red-500/10 p-4 text-red-400">
       {message}
    </div>
  );
};

export default ErrorAlert;