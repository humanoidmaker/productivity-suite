import { useState, useRef, useCallback } from "react";
import type { SlideElement } from "@/types/presentation";

interface Props {
  elements: SlideElement[];
  selectedElementIdx: number | null;
  onSelectElement: (idx: number | null) => void;
  onUpdateElement: (idx: number, updates: Partial<SlideElement>) => void;
  aspectRatio: "16:9" | "4:3";
  backgroundColor?: string;
}

export function SlideCanvas({ elements, selectedElementIdx, onSelectElement, onUpdateElement, aspectRatio, backgroundColor = "#ffffff" }: Props) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [dragging, setDragging] = useState<{ idx: number; startX: number; startY: number; origX: number; origY: number } | null>(null);

  const w = aspectRatio === "16:9" ? 960 : 800;
  const h = aspectRatio === "16:9" ? 540 : 600;

  const handleMouseDown = useCallback((e: React.MouseEvent, idx: number) => {
    e.stopPropagation();
    onSelectElement(idx);
    const el = elements[idx];
    setDragging({ idx, startX: e.clientX, startY: e.clientY, origX: el.x, origY: el.y });
  }, [elements, onSelectElement]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dragging) return;
    const scale = (canvasRef.current?.clientWidth || w) / w;
    const dx = (e.clientX - dragging.startX) / scale;
    const dy = (e.clientY - dragging.startY) / scale;
    onUpdateElement(dragging.idx, { x: dragging.origX + dx, y: dragging.origY + dy });
  }, [dragging, onUpdateElement, w]);

  const handleMouseUp = useCallback(() => { setDragging(null); }, []);

  return (
    <div className="flex-1 flex items-center justify-center bg-gray-200 p-8 overflow-auto">
      <div
        ref={canvasRef}
        className="relative shadow-lg"
        style={{ aspectRatio: `${w}/${h}`, width: "100%", maxWidth: w, backgroundColor, overflow: "hidden" }}
        onClick={() => onSelectElement(null)}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {elements.map((el, idx) => {
          const isSelected = idx === selectedElementIdx;
          const scaleX = 100 / w;
          const scaleY = 100 / h;

          return (
            <div
              key={idx}
              onMouseDown={e => handleMouseDown(e, idx)}
              className={`absolute cursor-move ${isSelected ? "ring-2 ring-blue-500" : ""}`}
              style={{
                left: `${el.x * scaleX}%`,
                top: `${el.y * scaleY}%`,
                width: `${el.width * scaleX}%`,
                height: `${el.height * scaleY}%`,
                transform: el.rotation ? `rotate(${el.rotation}deg)` : undefined,
                opacity: el.opacity ?? 1,
              }}
            >
              {el.type === "textbox" && (
                <div className="w-full h-full flex items-center p-2 overflow-hidden" style={{
                  fontSize: `${(el.fontSize || 18) * 0.8}px`,
                  fontWeight: el.bold ? 700 : 400,
                  fontStyle: el.italic ? "italic" : "normal",
                  color: el.color || "#000",
                  textAlign: (el.textAlign as "left" | "center" | "right") || "left",
                }}>
                  {el.text || "Text"}
                </div>
              )}

              {el.type === "shape" && (
                <div className="w-full h-full rounded" style={{
                  backgroundColor: el.fill || "#3b82f6",
                  border: el.stroke ? `${el.strokeWidth || 2}px solid ${el.stroke}` : "none",
                  borderRadius: el.shape === "circle" ? "50%" : el.shape === "rounded_rect" ? "12px" : "0",
                }} />
              )}

              {el.type === "image" && el.src && (
                <img src={el.src} alt="" className="w-full h-full object-contain" draggable={false} />
              )}

              {/* Resize handles */}
              {isSelected && (
                <>
                  {[
                    "top-0 left-0 cursor-nw-resize", "top-0 right-0 cursor-ne-resize",
                    "bottom-0 left-0 cursor-sw-resize", "bottom-0 right-0 cursor-se-resize",
                    "top-0 left-1/2 -translate-x-1/2 cursor-n-resize", "bottom-0 left-1/2 -translate-x-1/2 cursor-s-resize",
                    "top-1/2 left-0 -translate-y-1/2 cursor-w-resize", "top-1/2 right-0 -translate-y-1/2 cursor-e-resize",
                  ].map((cls, i) => (
                    <div key={i} className={`absolute ${cls} w-2 h-2 bg-white border-2 border-blue-500 rounded-sm`} />
                  ))}
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
