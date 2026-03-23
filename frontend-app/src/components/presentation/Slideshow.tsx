import { useState, useEffect, useCallback } from "react";
import type { SlideInfo, SlideElement } from "@/types/presentation";

interface Props {
  slides: SlideInfo[];
  elements: Record<string, SlideElement[]>;
  onExit: () => void;
  backgroundColor?: string;
}

export function Slideshow({ slides, elements, onExit, backgroundColor = "#ffffff" }: Props) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showBlack, setShowBlack] = useState(false);
  const [showWhite, setShowWhite] = useState(false);

  const visibleSlides = slides.filter(s => !s.hidden);
  const slide = visibleSlides[currentSlide];
  const slideElements = slide ? (elements[slide.id] || []) : [];

  const next = useCallback(() => {
    setShowBlack(false); setShowWhite(false);
    setCurrentSlide(prev => Math.min(prev + 1, visibleSlides.length - 1));
  }, [visibleSlides.length]);

  const prev = useCallback(() => {
    setShowBlack(false); setShowWhite(false);
    setCurrentSlide(prev => Math.max(prev - 1, 0));
  }, []);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onExit();
      else if (e.key === "ArrowRight" || e.key === " " || e.key === "Enter") next();
      else if (e.key === "ArrowLeft" || e.key === "Backspace") prev();
      else if (e.key === "b" || e.key === "B") { setShowBlack(v => !v); setShowWhite(false); }
      else if (e.key === "w" || e.key === "W") { setShowWhite(v => !v); setShowBlack(false); }
    };
    window.addEventListener("keydown", handler);

    // Request fullscreen
    document.documentElement.requestFullscreen?.().catch(() => {});

    return () => {
      window.removeEventListener("keydown", handler);
      if (document.fullscreenElement) document.exitFullscreen?.().catch(() => {});
    };
  }, [next, prev, onExit]);

  if (showBlack) return <div className="fixed inset-0 z-[9999] bg-black cursor-none" onClick={next} />;
  if (showWhite) return <div className="fixed inset-0 z-[9999] bg-white cursor-none" onClick={next} />;

  return (
    <div className="fixed inset-0 z-[9999] bg-black flex items-center justify-center cursor-none" onClick={next}>
      {/* Slide */}
      <div className="relative w-full h-full flex items-center justify-center" style={{ backgroundColor }}>
        <div className="relative" style={{ width: "100vw", height: "56.25vw", maxHeight: "100vh", maxWidth: "177.78vh" }}>
          {slideElements.map((el, idx) => (
            <div
              key={idx}
              className="absolute"
              style={{
                left: `${(el.x / 960) * 100}%`,
                top: `${(el.y / 540) * 100}%`,
                width: `${(el.width / 960) * 100}%`,
                height: `${(el.height / 540) * 100}%`,
                opacity: el.opacity ?? 1,
              }}
            >
              {el.type === "textbox" && (
                <div className="w-full h-full flex items-center p-2" style={{
                  fontSize: `${(el.fontSize || 24) * 1.5}px`,
                  fontWeight: el.bold ? 700 : 400,
                  fontStyle: el.italic ? "italic" : "normal",
                  color: el.color || "#000",
                  textAlign: (el.textAlign as CanvasTextAlign) || "left",
                }}>
                  {el.text}
                </div>
              )}
              {el.type === "shape" && (
                <div className="w-full h-full" style={{
                  backgroundColor: el.fill || "#3b82f6",
                  borderRadius: el.shape === "circle" ? "50%" : "0",
                }} />
              )}
              {el.type === "image" && el.src && (
                <img src={el.src} alt="" className="w-full h-full object-contain" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Slide counter */}
      <div className="absolute bottom-4 right-4 text-white/40 text-xs font-mono">
        {currentSlide + 1} / {visibleSlides.length}
      </div>
    </div>
  );
}
