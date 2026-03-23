import { useState, useEffect } from "react";
import { FunctionSquare } from "lucide-react";

interface Props {
  cellRef: string;
  value: string;
  onChange: (value: string) => void;
  onCommit: () => void;
}

export function FormulaBar({ cellRef, value, onChange, onCommit }: Props) {
  return (
    <div className="flex items-center h-8 border-b border-gray-200 bg-white shrink-0">
      {/* Cell reference display */}
      <div className="w-20 h-full flex items-center justify-center border-r border-gray-200 text-xs font-mono font-medium text-gray-700 bg-gray-50 shrink-0 select-none">
        {cellRef}
      </div>

      {/* Function icon */}
      <div className="w-8 h-full flex items-center justify-center border-r border-gray-200 shrink-0">
        <FunctionSquare className="h-3.5 w-3.5 text-gray-400" />
      </div>

      {/* Formula/value input */}
      <input
        value={value}
        onChange={e => onChange(e.target.value)}
        onKeyDown={e => {
          if (e.key === "Enter") { onCommit(); e.preventDefault(); }
          if (e.key === "Escape") { e.preventDefault(); }
        }}
        className="flex-1 h-full px-2 text-[12px] font-mono border-none outline-none"
        placeholder="Enter value or formula (e.g. =SUM(A1:A10))"
      />
    </div>
  );
}
