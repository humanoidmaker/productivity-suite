import { useState, useRef, useCallback, useEffect, useMemo } from "react";
import type { CellData, CellFormat } from "@/types/spreadsheet";

interface Props {
  cells: Record<string, CellData>;
  onCellChange: (ref: string, value: string) => void;
  onSelectionChange: (ref: string) => void;
  selectedCell: string;
  rowCount?: number;
  colCount?: number;
}

const DEFAULT_COL_WIDTH = 100;
const DEFAULT_ROW_HEIGHT = 28;
const HEADER_WIDTH = 50;
const HEADER_HEIGHT = 28;

function colToLetter(col: number): string {
  let result = "";
  let c = col + 1;
  while (c > 0) {
    c--;
    result = String.fromCharCode(65 + (c % 26)) + result;
    c = Math.floor(c / 26);
  }
  return result;
}

function cellRef(row: number, col: number): string {
  return `${colToLetter(col)}${row + 1}`;
}

export function SheetGrid({ cells, onCellChange, onSelectionChange, selectedCell, rowCount = 100, colCount = 26 }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [editingCell, setEditingCell] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const [scrollTop, setScrollTop] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const [containerSize, setContainerSize] = useState({ width: 800, height: 600 });

  // Visible range based on scroll
  const visibleStartRow = Math.floor(scrollTop / DEFAULT_ROW_HEIGHT);
  const visibleEndRow = Math.min(rowCount - 1, visibleStartRow + Math.ceil(containerSize.height / DEFAULT_ROW_HEIGHT) + 2);
  const visibleStartCol = Math.floor(scrollLeft / DEFAULT_COL_WIDTH);
  const visibleEndCol = Math.min(colCount - 1, visibleStartCol + Math.ceil(containerSize.width / DEFAULT_COL_WIDTH) + 2);

  // Track container size
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      setContainerSize({ width, height });
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
    setScrollLeft(e.currentTarget.scrollLeft);
  }, []);

  const handleCellClick = useCallback((ref: string) => {
    onSelectionChange(ref);
    setEditingCell(null);
  }, [onSelectionChange]);

  const handleCellDoubleClick = useCallback((ref: string) => {
    setEditingCell(ref);
    const cell = cells[ref];
    setEditValue(cell?.formula ? `=${cell.formula}` : String(cell?.value ?? ""));
  }, [cells]);

  const commitEdit = useCallback(() => {
    if (editingCell) {
      onCellChange(editingCell, editValue);
      setEditingCell(null);
    }
  }, [editingCell, editValue, onCellChange]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (editingCell) {
      if (e.key === "Enter") { commitEdit(); e.preventDefault(); }
      if (e.key === "Escape") { setEditingCell(null); e.preventDefault(); }
      if (e.key === "Tab") {
        commitEdit();
        e.preventDefault();
        // Move to next cell
        const match = selectedCell.match(/^([A-Z]+)(\d+)$/);
        if (match) {
          const col = match[1].charCodeAt(0) - 65;
          const row = parseInt(match[2]) - 1;
          const nextRef = cellRef(row, col + 1);
          onSelectionChange(nextRef);
        }
      }
      return;
    }

    // Navigation in non-edit mode
    const match = selectedCell.match(/^([A-Z]+)(\d+)$/);
    if (!match) return;
    let col = 0;
    for (let i = 0; i < match[1].length; i++) {
      col = col * 26 + (match[1].charCodeAt(i) - 64);
    }
    col--;
    let row = parseInt(match[2]) - 1;

    if (e.key === "ArrowDown") { row = Math.min(rowCount - 1, row + 1); e.preventDefault(); }
    else if (e.key === "ArrowUp") { row = Math.max(0, row - 1); e.preventDefault(); }
    else if (e.key === "ArrowRight" || e.key === "Tab") { col = Math.min(colCount - 1, col + 1); e.preventDefault(); }
    else if (e.key === "ArrowLeft") { col = Math.max(0, col - 1); e.preventDefault(); }
    else if (e.key === "Enter") { handleCellDoubleClick(selectedCell); e.preventDefault(); return; }
    else if (e.key === "Delete" || e.key === "Backspace") { onCellChange(selectedCell, ""); return; }
    else if (e.key.length === 1 && !e.ctrlKey && !e.metaKey) {
      // Start typing in cell
      setEditingCell(selectedCell);
      setEditValue(e.key);
      e.preventDefault();
      return;
    } else return;

    onSelectionChange(cellRef(row, col));
  }, [selectedCell, editingCell, commitEdit, onSelectionChange, onCellChange, handleCellDoubleClick, rowCount, colCount]);

  const totalWidth = colCount * DEFAULT_COL_WIDTH + HEADER_WIDTH;
  const totalHeight = rowCount * DEFAULT_ROW_HEIGHT + HEADER_HEIGHT;

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-auto relative outline-none border-t border-gray-200"
      onScroll={handleScroll}
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      <div style={{ width: totalWidth, height: totalHeight, position: "relative" }}>
        {/* Column headers */}
        <div className="sticky top-0 z-20 flex" style={{ height: HEADER_HEIGHT }}>
          <div className="sticky left-0 z-30 bg-gray-100 border-b border-r border-gray-300" style={{ width: HEADER_WIDTH, height: HEADER_HEIGHT }} />
          {Array.from({ length: visibleEndCol - visibleStartCol + 1 }, (_, i) => {
            const col = visibleStartCol + i;
            return (
              <div
                key={col}
                className="bg-gray-100 border-b border-r border-gray-300 flex items-center justify-center text-[11px] font-medium text-gray-500 select-none"
                style={{ position: "absolute", left: HEADER_WIDTH + col * DEFAULT_COL_WIDTH, width: DEFAULT_COL_WIDTH, height: HEADER_HEIGHT }}
              >
                {colToLetter(col)}
              </div>
            );
          })}
        </div>

        {/* Row headers + cells */}
        {Array.from({ length: visibleEndRow - visibleStartRow + 1 }, (_, ri) => {
          const row = visibleStartRow + ri;
          const y = HEADER_HEIGHT + row * DEFAULT_ROW_HEIGHT;

          return (
            <div key={row} style={{ position: "absolute", top: y, left: 0, height: DEFAULT_ROW_HEIGHT, width: totalWidth }}>
              {/* Row header */}
              <div
                className="sticky left-0 z-10 bg-gray-100 border-b border-r border-gray-300 flex items-center justify-center text-[11px] font-medium text-gray-500 select-none"
                style={{ position: "absolute", width: HEADER_WIDTH, height: DEFAULT_ROW_HEIGHT }}
              >
                {row + 1}
              </div>

              {/* Cells */}
              {Array.from({ length: visibleEndCol - visibleStartCol + 1 }, (_, ci) => {
                const col = visibleStartCol + ci;
                const ref = cellRef(row, col);
                const cell = cells[ref];
                const isSelected = ref === selectedCell;
                const isEditing = ref === editingCell;
                const fmt = cell?.format;

                return (
                  <div
                    key={col}
                    onClick={() => handleCellClick(ref)}
                    onDoubleClick={() => handleCellDoubleClick(ref)}
                    className={`absolute border-b border-r border-gray-200 overflow-hidden ${isSelected ? "ring-2 ring-blue-500 z-10" : ""}`}
                    style={{
                      left: HEADER_WIDTH + col * DEFAULT_COL_WIDTH,
                      width: DEFAULT_COL_WIDTH,
                      height: DEFAULT_ROW_HEIGHT,
                      backgroundColor: fmt?.backgroundColor || "white",
                    }}
                  >
                    {isEditing ? (
                      <input
                        autoFocus
                        value={editValue}
                        onChange={e => setEditValue(e.target.value)}
                        onBlur={commitEdit}
                        className="w-full h-full px-1.5 text-[12px] border-none outline-none bg-white"
                      />
                    ) : (
                      <div
                        className="w-full h-full px-1.5 flex items-center text-[12px] truncate"
                        style={{
                          fontWeight: fmt?.bold ? 700 : 400,
                          fontStyle: fmt?.italic ? "italic" : "normal",
                          textAlign: fmt?.textAlign || "left",
                          color: fmt?.textColor || "#1a1a2e",
                        }}
                      >
                        {cell?.value != null ? String(cell.value) : ""}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}
