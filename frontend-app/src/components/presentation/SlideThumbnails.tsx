import { Plus } from "lucide-react";
import type { SlideInfo, SlideElement } from "@/types/presentation";

interface Props {
  slides: SlideInfo[];
  elements: Record<string, SlideElement[]>;
  activeSlide: number;
  onSelect: (index: number) => void;
  onAdd: () => void;
  onReorder: (from: number, to: number) => void;
}

export function SlideThumbnails({ slides, elements, activeSlide, onSelect, onAdd }: Props) {
  return (
    <div className="w-48 bg-gray-50 border-r border-gray-200 flex flex-col shrink-0 overflow-y-auto">
      <div className="p-2 space-y-1.5">
        {slides.map((slide, idx) => {
          const slideElements = elements[slide.id] || [];
          const isActive = idx === activeSlide;

          return (
            <button
              key={slide.id}
              onClick={() => onSelect(idx)}
              className={`w-full rounded-lg border-2 transition-colors overflow-hidden ${
                isActive ? "border-blue-500" : "border-transparent hover:border-gray-300"
              }`}
            >
              <div className="relative">
                {/* Slide number */}
                <div className="absolute top-1 left-1 text-[9px] font-medium text-gray-400 bg-white/80 rounded px-1">{idx + 1}</div>
                {/* Mini preview */}
                <div className="bg-white aspect-video flex items-center justify-center text-[8px] text-gray-400 p-2">
                  {slideElements.length > 0 ? (
                    <div className="text-left w-full truncate">
                      {slideElements.filter(e => e.type === "textbox").map(e => e.text).filter(Boolean).join(" · ").slice(0, 40) || "Slide"}
                    </div>
                  ) : (
                    `Slide ${idx + 1}`
                  )}
                </div>
                {slide.hidden && (
                  <div className="absolute inset-0 bg-gray-500/30 flex items-center justify-center text-[8px] text-white font-medium">HIDDEN</div>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Add slide */}
      <button onClick={onAdd} className="mx-2 mb-2 mt-auto py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-400 hover:border-blue-400 hover:text-blue-500 transition-colors flex items-center justify-center gap-1 text-[10px]">
        <Plus className="h-3 w-3" /> Add Slide
      </button>
    </div>
  );
}
