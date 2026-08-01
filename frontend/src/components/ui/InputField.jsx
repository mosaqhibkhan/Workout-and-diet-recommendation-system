const InputField = ({
  label,
  type,
  placeholder,
  value,
  onChange,
  min,
  max,
  step,
}) => {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-xs font-semibold uppercase tracking-[0.12em] text-gray-400">
        {label}
      </label>

      <input
        type={type}
        placeholder={placeholder}
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={onChange}
        className="rounded-lg border border-gray-700 bg-[#111118] px-4 py-3 text-white outline-none transition focus:border-lime-300 focus:ring-2 focus:ring-lime-300/20"
      />
    </div>
  );
};

export default InputField;