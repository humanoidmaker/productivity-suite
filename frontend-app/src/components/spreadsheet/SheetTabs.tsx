import { useState } from "react";
import { Plus, MoreHorizontal } from "lucide-react";
import type { SheetInfo } from "@/types/spreadsheet";

interface Props {
  sheets: SheetInfo[];
  activeSheet: number;
  onSelect: (index: number) => void;
  onAdd: () => void;
  onRename: (index: number, name: string) => void;
  onDelete: (index: number) => void;
}

export function SheetTabs({ sheets, activeSheet, onSelect, onAdd, onRename, onDelete }: Props) {
  const [contextMenu, setContextMenu] = useState<{ index: number; x: number; y: number } | null>(null);
  const [renamingIdx, setRenamingIdx] = useState<number | null>(null);
  const [renameName, setRenameName] = useState("");

  return (
    <div className="flex items-center h-8 bg-gray-50 border-t border-gray-200 shrink-0 relative">
      {sheets.map((sheet, idx) => (
        <button
          key={idx}
          onClick={() => onSelect(idx)}
          onDoubleClick={() => { setRenamingIdx(idx); setRenameName(sheet.name); }}
          onContextMenu={e => { e.preventDefault(); setContextMenu({ index: idx, x: e.clientX, y: e.clientY }); }}
          className={`h-full px-4 text-[11px] font-medium border-r border-gray-200 flex items-center gap-1.5 transition-colors ${
            idx === activeSheet ? "bg-white text-gray-900 border-t-2 border-t-blue-500" : "text-gray-500 hover:bg-gray-100"
          }`}
          style={sheet.color ? { borderTopColor: sheet.color } : undefined}
        >
          {renamingIdx === idx ? (
            <input
              autoFocus
              value={renameName}
              onChange={e => setRenameName(e.target.value)}
              onBlur={() => { onRename(idx, renameName); setRenamingIdx(null); }}
              onKeyDown={e => { if (e.key === "Enter") { onRename(idx, renameName); setRenamingIdx(null); } }}
              className="w-20 text-[11px] bg-transparent border-b border-blue-400 outline-none"
              onClick={e => e.stopPropagation()}
            />
          ) : (
            sheet.name
          )}
        </button>
      ))}

      {/* Add sheet */}
      <button onClick={onAdd} className="h-full px-3 text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors" title="Add sheet">
        <Plus className="h-3.5 w-3.5" />
      </button>

      {/* Context menu */}
      {contextMenu && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setContextMenu(null)} />
          <div className="fixed z-50 bg-white border border-gray-200 rounded-lg shadow-xl py-1 w-36" style={{ left: contextMenu.x, top: contextMenu.y - 120 }}>
            <button onClick={() => { setRenamingIdx(contextMenu.index); setRenameName(sheets[contextMenu.index].name); setContextMenu(null); }} className="w-full text-left px-3 py-1.5 text-xs hover:bg-gray-50">Rename</button>
            <button onClick={() => { onAdd(); setContextMenu(null); }} className="w-full text-left px-3 py-1.5 text-xs hover:bg-gray-50">Duplicate</button>
            {sheets.length > 1 && (
              <button onClick={() => { onDelete(contextMenu.index); setContextMenu(null); }} className="w-full text-left px-3 py-1.5 text-xs text-red-600 hover:bg-red-50">Delete</button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
