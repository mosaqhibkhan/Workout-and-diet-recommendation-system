const SelectField = ({
  label,
  value,
  onChange,
  options,
}) => {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-xs font-semibold uppercase tracking-[0.12em] text-gray-400">
        {label}
      </label>

      <select
        value={value}
        onChange={onChange}
        className="rounded-lg border border-gray-700 bg-[#111118] px-4 py-3 text-white outline-none transition focus:border-lime-300 focus:ring-2 focus:ring-lime-300/20"
      >
        {options.map((item) => (
          <option key={item.value} value={item.value}>
            {item.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default SelectField;