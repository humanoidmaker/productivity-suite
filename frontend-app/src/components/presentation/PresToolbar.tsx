import { Type, Square, Circle, Image, Minus, Play, Download, Bold, Italic, AlignLeft, AlignCenter, Paintbrush } from "lucide-react";
import type { SlideElement } from "@/types/presentation";

interface Props {
  onInsertElement: (element: SlideElement) => void;
  onStartSlideshow: () => void;
  selectedElement: SlideElement | null;
  onUpdateElement: (updates: Partial<SlideElement>) => void;
}

export function PresToolbar({ onInsertElement, onStartSlideshow, selectedElement, onUpdateElement }: Props) {
  const btn = (onClick: () => void, icon: React.ReactNode, title: string) => (
    <button onClick={onClick} title={title} className="p-1.5 rounded hover:bg-gray-100 text-gray-600 transition-colors">{icon}</button>
  );

  const sep = () => <div className="w-px h-5 bg-gray-200 mx-0.5" />;

  const insertTextbox = () => onInsertElement({ type: "textbox", x: 200, y: 200, width: 300, height: 60, text: "Click to edit", fontSize: 24 });
  const insertRect = () => onInsertElement({ type: "shape", x: 200, y: 200, width: 200, height: 150, shape: "rectangle", fill: "#3b82f6" });
  const insertCircle = () => onInsertElement({ type: "shape", x: 200, y: 200, width: 150, height: 150, shape: "circle", fill: "#22c55e" });
  const insertImage = () => {
    const url = prompt("Enter image URL:");
    if (url) onInsertElement({ type: "image", x: 200, y: 150, width: 300, height: 200, src: url });
  };

  return (
    <div className="flex items-center gap-0.5 px-3 py-1 border-b border-gray-200 bg-white shrink-0 flex-wrap">
      {/* Insert group */}
      {btn(insertTextbox, <Type className="h-4 w-4" />, "Insert Text Box")}
      {btn(insertRect, <Square className="h-4 w-4" />, "Insert Rectangle")}
      {btn(() => onInsertElement({ type: "shape", x: 200, y: 200, width: 150, height: 150, shape: "circle", fill: "#22c55e" }), <Circle className="h-4 w-4" />, "Insert Circle")}
      {btn(insertImage, <Image className="h-4 w-4" />, "Insert Image")}
      {btn(() => onInsertElement({ type: "shape", x: 100, y: 300, width: 760, height: 3, shape: "line", fill: "#64748b" }), <Minus className="h-4 w-4" />, "Insert Line")}

      {sep()}

      {/* Format selected element */}
      {selectedElement?.type === "textbox" && (
        <>
          {btn(() => onUpdateElement({ bold: !selectedElement.bold }), <Bold className={`h-4 w-4 ${selectedElement.bold ? "text-blue-600" : ""}`} />, "Bold")}
          {btn(() => onUpdateElement({ italic: !selectedElement.italic }), <Italic className={`h-4 w-4 ${selectedElement.italic ? "text-blue-600" : ""}`} />, "Italic")}
          {btn(() => onUpdateElement({ textAlign: "left" }), <AlignLeft className="h-4 w-4" />, "Align Left")}
          {btn(() => onUpdateElement({ textAlign: "center" }), <AlignCenter className="h-4 w-4" />, "Align Center")}
          {sep()}
        </>
      )}

      {/* Fill color for any element */}
      {selectedElement && (
        <label className="relative cursor-pointer" title="Fill color">
          <Paintbrush className="h-4 w-4 text-gray-600" />
          <input type="color" value={selectedElement.fill || "#3b82f6"} className="absolute inset-0 opacity-0 w-full h-full cursor-pointer"
            onChange={e => onUpdateElement({ fill: e.target.value })} />
        </label>
      )}

      <div className="flex-1" />

      {/* Present button */}
      <button onClick={onStartSlideshow} className="flex items-center gap-1.5 px-4 h-8 bg-pres text-white text-xs font-medium rounded-lg hover:bg-pres/90 transition-colors">
        <Play className="h-3.5 w-3.5" /> Present
      </button>
    </div>
  );
}
