import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Save, Download, Loader2, Check } from "lucide-react";
import { getSpreadsheet, updateSpreadsheet } from "@/api/spreadsheetsApi";
import { SheetGrid } from "@/components/spreadsheet/SheetGrid";
import { FormulaBar } from "@/components/spreadsheet/FormulaBar";
import { SheetTabs } from "@/components/spreadsheet/SheetTabs";
import { SheetToolbar } from "@/components/spreadsheet/SheetToolbar";
import { SheetStatusBar } from "@/components/spreadsheet/SheetStatusBar";
import type { Spreadsheet, SheetInfo, CellData } from "@/types/spreadsheet";

export default function SpreadsheetEditor() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("Untitled Spreadsheet");
  const [sheets, setSheets] = useState<SheetInfo[]>([{ name: "Sheet1", index: 0, visible: true, color: null }]);
  const [activeSheet, setActiveSheet] = useState(0);
  const [cells, setCells] = useState<Record<string, Record<string, CellData>>>({ Sheet1: {} });
  const [selectedCell, setSelectedCell] = useState("A1");
  const [formulaValue, setFormulaValue] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const autoSaveTimer = useRef<ReturnType<typeof setTimeout>>();

  // Load spreadsheet
  useEffect(() => {
    if (!id) return;
    getSpreadsheet(id)
      .then(data => {
        setTitle(data.title);
        if (data.sheets_meta_json) {
          const meta = data.sheets_meta_json as Record<string, unknown>;
          if (Array.isArray(meta.sheets)) setSheets(meta.sheets as SheetInfo[]);
          if (meta.cells) setCells(meta.cells as Record<string, Record<string, CellData>>);
        }
      })
      .catch(() => navigate("/"))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const currentSheetName = sheets[activeSheet]?.name || "Sheet1";
  const currentCells = cells[currentSheetName] || {};

  // Update formula bar when selection changes
  useEffect(() => {
    const cell = currentCells[selectedCell];
    setFormulaValue(cell?.formula ? `=${cell.formula}` : String(cell?.value ?? ""));
  }, [selectedCell, currentCells]);

  const handleCellChange = useCallback((ref: string, value: string) => {
    setCells(prev => {
      const sheetCells = { ...(prev[currentSheetName] || {}) };
      if (!value) {
        delete sheetCells[ref];
      } else if (value.startsWith("=")) {
        sheetCells[ref] = { value: value, formula: value.slice(1) };
      } else {
        const num = Number(value);
        sheetCells[ref] = { value: isNaN(num) ? value : num };
      }
      return { ...prev, [currentSheetName]: sheetCells };
    });
    setSaved(false);
    clearTimeout(autoSaveTimer.current);
    autoSaveTimer.current = setTimeout(() => handleSave(), 5000);
  }, [currentSheetName]);

  const handleFormulaCommit = useCallback(() => {
    handleCellChange(selectedCell, formulaValue);
  }, [selectedCell, formulaValue, handleCellChange]);

  const handleFormat = useCallback((format: Record<string, unknown>) => {
    setCells(prev => {
      const sheetCells = { ...(prev[currentSheetName] || {}) };
      const existing = sheetCells[selectedCell] || { value: null };
      sheetCells[selectedCell] = { ...existing, format: { ...(existing.format || {}), ...format } as CellData["format"] };
      return { ...prev, [currentSheetName]: sheetCells };
    });
  }, [currentSheetName, selectedCell]);

  const handleAddSheet = useCallback(() => {
    const name = `Sheet${sheets.length + 1}`;
    setSheets(prev => [...prev, { name, index: prev.length, visible: true, color: null }]);
    setCells(prev => ({ ...prev, [name]: {} }));
    setActiveSheet(sheets.length);
  }, [sheets]);

  const handleRenameSheet = useCallback((idx: number, name: string) => {
    if (!name.trim()) return;
    const oldName = sheets[idx].name;
    setSheets(prev => prev.map((s, i) => i === idx ? { ...s, name } : s));
    setCells(prev => {
      const next = { ...prev };
      next[name] = next[oldName] || {};
      delete next[oldName];
      return next;
    });
  }, [sheets]);

  const handleDeleteSheet = useCallback((idx: number) => {
    if (sheets.length <= 1) return;
    const name = sheets[idx].name;
    setSheets(prev => prev.filter((_, i) => i !== idx));
    setCells(prev => { const next = { ...prev }; delete next[name]; return next; });
    if (activeSheet >= idx && activeSheet > 0) setActiveSheet(activeSheet - 1);
  }, [sheets, activeSheet]);

  const handleSave = useCallback(async () => {
    if (!id) return;
    setSaving(true);
    try {
      await updateSpreadsheet(id, {
        title,
        sheets_meta_json: { sheets, cells } as unknown as Record<string, unknown>,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch { /* silent */ }
    finally { setSaving(false); }
  }, [id, title, sheets, cells]);

  // Ctrl+S
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "s") { e.preventDefault(); handleSave(); }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleSave]);

  if (loading) {
    return <div className="h-screen flex items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-sheet" /></div>;
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Top bar */}
      <div className="h-11 bg-white border-b border-gray-200 flex items-center px-3 gap-3 shrink-0">
        <button onClick={() => navigate("/")} className="p-1.5 rounded hover:bg-gray-100 text-gray-500"><ArrowLeft className="h-4 w-4" /></button>
        <div className="h-6 w-6 rounded bg-sheet/10 flex items-center justify-center"><span className="text-sheet text-[10px] font-bold">S</span></div>
        <input value={title} onChange={e => { setTitle(e.target.value); setSaved(false); }} onBlur={handleSave}
          className="text-sm font-medium text-gray-900 bg-transparent border-none focus:outline-none focus:bg-gray-50 rounded px-1 min-w-0 flex-1 max-w-md" />
        <div className="flex items-center gap-2 ml-auto">
          {saving && <Loader2 className="h-3.5 w-3.5 animate-spin text-gray-400" />}
          {saved && <Check className="h-3.5 w-3.5 text-green-500" />}
          <button onClick={handleSave} className="flex items-center gap-1 px-3 h-7 text-xs text-gray-600 hover:bg-gray-100 rounded"><Save className="h-3 w-3" /> Save</button>
        </div>
      </div>

      {/* Toolbar */}
      <SheetToolbar onFormat={handleFormat} onUndo={() => {}} onRedo={() => {}} />

      {/* Formula bar */}
      <FormulaBar cellRef={selectedCell} value={formulaValue} onChange={setFormulaValue} onCommit={handleFormulaCommit} />

      {/* Grid */}
      <SheetGrid cells={currentCells} onCellChange={handleCellChange} onSelectionChange={setSelectedCell} selectedCell={selectedCell} />

      {/* Sheet tabs */}
      <SheetTabs sheets={sheets} activeSheet={activeSheet} onSelect={setActiveSheet} onAdd={handleAddSheet} onRename={handleRenameSheet} onDelete={handleDeleteSheet} />

      {/* Status bar */}
      <SheetStatusBar cells={currentCells} selectedCell={selectedCell} />
    </div>
  );
}
