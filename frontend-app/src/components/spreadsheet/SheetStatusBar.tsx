import type { CellData } from "@/types/spreadsheet";

interface Props {
  cells: Record<string, CellData>;
  selectedCell: string;
}

export function SheetStatusBar({ cells, selectedCell }: Props) {
  // Calculate SUM/AVERAGE/COUNT of selected (single cell for now)
  const cell = cells[selectedCell];
  const val = cell?.value;
  const isNum = typeof val === "number";

  return (
    <div className="h-6 bg-gray-50 border-t border-gray-200 flex items-center px-4 text-[10px] text-gray-500 gap-6 shrink-0">
      {isNum && (
        <>
          <span>SUM: {val}</span>
          <span>AVG: {val}</span>
          <span>COUNT: 1</span>
        </>
      )}
      <div className="flex-1" />
      <span>100%</span>
    </div>
  );
}
