import { Bold, Italic, Underline, AlignLeft, AlignCenter, AlignRight, Paintbrush, Type, Undo2, Redo2, Download } from "lucide-react";
import { useState } from "react";

interface Props {
  onFormat: (format: Record<string, unknown>) => void;
  onUndo: () => void;
  onRedo: () => void;
}

export function SheetToolbar({ onFormat, onUndo, onRedo }: Props) {
  const btn = (onClick: () => void, icon: React.ReactNode, title: string, active = false) => (
    <button onClick={onClick} title={title}
      className={`p-1.5 rounded hover:bg-gray-100 transition-colors ${active ? "bg-blue-100 text-blue-700" : "text-gray-600"}`}>
      {icon}
    </button>
  );

  const sep = () => <div className="w-px h-5 bg-gray-200 mx-0.5" />;

  return (
    <div className="flex items-center gap-0.5 px-3 py-1 border-b border-gray-200 bg-white shrink-0 flex-wrap">
      {btn(onUndo, <Undo2 className="h-4 w-4" />, "Undo")}
      {btn(onRedo, <Redo2 className="h-4 w-4" />, "Redo")}

      {sep()}

      {/* Font size */}
      <select className="h-7 px-1 border border-gray-200 rounded text-[11px] text-gray-700" onChange={e => onFormat({ fontSize: parseInt(e.target.value) })}>
        {[8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 36].map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>

      {sep()}

      {btn(() => onFormat({ bold: true }), <Bold className="h-4 w-4" />, "Bold")}
      {btn(() => onFormat({ italic: true }), <Italic className="h-4 w-4" />, "Italic")}
      {btn(() => onFormat({ underline: true }), <Underline className="h-4 w-4" />, "Underline")}

      {sep()}

      {/* Text color */}
      <label className="relative cursor-pointer" title="Text color">
        <Type className="h-4 w-4 text-gray-600" />
        <input type="color" className="absolute inset-0 opacity-0 w-full h-full cursor-pointer" onChange={e => onFormat({ textColor: e.target.value })} />
        <div className="h-0.5 w-4 bg-red-500 mt-0.5" />
      </label>

      {/* Fill color */}
      <label className="relative cursor-pointer ml-1" title="Fill color">
        <Paintbrush className="h-4 w-4 text-gray-600" />
        <input type="color" className="absolute inset-0 opacity-0 w-full h-full cursor-pointer" onChange={e => onFormat({ backgroundColor: e.target.value })} />
      </label>

      {sep()}

      {btn(() => onFormat({ textAlign: "left" }), <AlignLeft className="h-4 w-4" />, "Align Left")}
      {btn(() => onFormat({ textAlign: "center" }), <AlignCenter className="h-4 w-4" />, "Align Center")}
      {btn(() => onFormat({ textAlign: "right" }), <AlignRight className="h-4 w-4" />, "Align Right")}
    </div>
  );
}
