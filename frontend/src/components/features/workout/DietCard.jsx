import DietList from "./DietList";

const DietCard = ({ diet }) => {
  return (
    <div className="overflow-hidden rounded-2xl border border-gray-800 bg-[#16161f] shadow-lg">
      <div className="border-b border-gray-800 p-6">
        <h2 className="text-2xl font-bold">
           Diet Plan
        </h2>
      </div>

      <DietList diet={diet} />
    </div>
  );
};

export default DietCard;