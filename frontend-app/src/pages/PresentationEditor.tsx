import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Save, Loader2, Check } from "lucide-react";
import { getPresentation, updatePresentation } from "@/api/presentationsApi";
import { SlideCanvas } from "@/components/presentation/SlideCanvas";
import { SlideThumbnails } from "@/components/presentation/SlideThumbnails";
import { PresToolbar } from "@/components/presentation/PresToolbar";
import { SpeakerNotes } from "@/components/presentation/SpeakerNotes";
import { PresStatusBar } from "@/components/presentation/PresStatusBar";
import { Slideshow } from "@/components/presentation/Slideshow";
import type { SlideInfo, SlideElement, PresentationTheme } from "@/types/presentation";

function newSlideId() { return `slide-${Date.now().toString(36)}`; }

export default function PresentationEditor() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("Untitled Presentation");
  const [slides, setSlides] = useState<SlideInfo[]>([{ id: newSlideId(), layout: "title", transition: "none", transitionDuration: 0.5, speakerNotes: "", hidden: false }]);
  const [elements, setElements] = useState<Record<string, SlideElement[]>>({});
  const [activeSlide, setActiveSlide] = useState(0);
  const [selectedElementIdx, setSelectedElementIdx] = useState<number | null>(null);
  const [theme, setTheme] = useState<PresentationTheme>({ primary: "#2563eb", secondary: "#64748b", accent: "#f59e0b", background: "#ffffff", text: "#1e293b", headingFont: "Inter", bodyFont: "Inter" });
  const [aspectRatio, setAspectRatio] = useState<"16:9" | "4:3">("16:9");
  const [showSlideshow, setShowSlideshow] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const autoSaveTimer = useRef<ReturnType<typeof setTimeout>>();

  // Load presentation
  useEffect(() => {
    if (!id) return;
    getPresentation(id)
      .then(data => {
        setTitle(data.title);
        setAspectRatio(data.aspect_ratio);
        if (data.theme_json) setTheme(data.theme_json);
        if (data.slides_meta_json) {
          const meta = data.slides_meta_json as Record<string, unknown>;
          if (Array.isArray(meta.slides)) setSlides(meta.slides as SlideInfo[]);
          if (meta.elements) setElements(meta.elements as Record<string, SlideElement[]>);
        }
      })
      .catch(() => navigate("/"))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const currentSlide = slides[activeSlide];
  const currentElements = currentSlide ? (elements[currentSlide.id] || []) : [];
  const selectedElement = selectedElementIdx !== null ? currentElements[selectedElementIdx] : null;

  const handleInsertElement = useCallback((element: SlideElement) => {
    if (!currentSlide) return;
    setElements(prev => ({
      ...prev,
      [currentSlide.id]: [...(prev[currentSlide.id] || []), element],
    }));
    setSelectedElementIdx(currentElements.length);
    setSaved(false);
  }, [currentSlide, currentElements.length]);

  const handleUpdateElement = useCallback((idx: number, updates: Partial<SlideElement>) => {
    if (!currentSlide) return;
    setElements(prev => ({
      ...prev,
      [currentSlide.id]: (prev[currentSlide.id] || []).map((el, i) => i === idx ? { ...el, ...updates } : el),
    }));
    setSaved(false);
  }, [currentSlide]);

  const handleUpdateSelectedElement = useCallback((updates: Partial<SlideElement>) => {
    if (selectedElementIdx !== null) handleUpdateElement(selectedElementIdx, updates);
  }, [selectedElementIdx, handleUpdateElement]);

  const handleAddSlide = useCallback(() => {
    const newId = newSlideId();
    setSlides(prev => [...prev, { id: newId, layout: "blank", transition: "none", transitionDuration: 0.5, speakerNotes: "", hidden: false }]);
    setActiveSlide(slides.length);
    setSelectedElementIdx(null);
  }, [slides.length]);

  const handleUpdateNotes = useCallback((notes: string) => {
    setSlides(prev => prev.map((s, i) => i === activeSlide ? { ...s, speakerNotes: notes } : s));
    setSaved(false);
  }, [activeSlide]);

  const handleSave = useCallback(async () => {
    if (!id) return;
    setSaving(true);
    try {
      await updatePresentation(id, {
        title,
        slides_meta_json: { slides, elements },
        theme_json: theme,
        aspect_ratio: aspectRatio,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch { /* silent */ }
    finally { setSaving(false); }
  }, [id, title, slides, elements, theme, aspectRatio]);

  // Ctrl+S
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "s") { e.preventDefault(); handleSave(); }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleSave]);

  // Delete selected element
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.key === "Delete" || e.key === "Backspace") && selectedElementIdx !== null && currentSlide && !(e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement)) {
        setElements(prev => ({
          ...prev,
          [currentSlide.id]: (prev[currentSlide.id] || []).filter((_, i) => i !== selectedElementIdx),
        }));
        setSelectedElementIdx(null);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [selectedElementIdx, currentSlide]);

  if (loading) {
    return <div className="h-screen flex items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-pres" /></div>;
  }

  if (showSlideshow) {
    return <Slideshow slides={slides} elements={elements} onExit={() => setShowSlideshow(false)} backgroundColor={theme.background} />;
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Top bar */}
      <div className="h-11 bg-white border-b border-gray-200 flex items-center px-3 gap-3 shrink-0">
        <button onClick={() => navigate("/")} className="p-1.5 rounded hover:bg-gray-100 text-gray-500"><ArrowLeft className="h-4 w-4" /></button>
        <div className="h-6 w-6 rounded bg-pres/10 flex items-center justify-center"><span className="text-pres text-[10px] font-bold">P</span></div>
        <input value={title} onChange={e => { setTitle(e.target.value); setSaved(false); }} onBlur={handleSave}
          className="text-sm font-medium text-gray-900 bg-transparent border-none focus:outline-none focus:bg-gray-50 rounded px-1 min-w-0 flex-1 max-w-md" />
        <div className="flex items-center gap-2 ml-auto">
          {saving && <Loader2 className="h-3.5 w-3.5 animate-spin text-gray-400" />}
          {saved && <Check className="h-3.5 w-3.5 text-green-500" />}
          <button onClick={handleSave} className="flex items-center gap-1 px-3 h-7 text-xs text-gray-600 hover:bg-gray-100 rounded"><Save className="h-3 w-3" /> Save</button>
        </div>
      </div>

      {/* Toolbar */}
      <PresToolbar
        onInsertElement={handleInsertElement}
        onStartSlideshow={() => setShowSlideshow(true)}
        selectedElement={selectedElement}
        onUpdateElement={handleUpdateSelectedElement}
      />

      {/* Main area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Slide thumbnails */}
        <SlideThumbnails
          slides={slides} elements={elements} activeSlide={activeSlide}
          onSelect={(idx) => { setActiveSlide(idx); setSelectedElementIdx(null); }}
          onAdd={handleAddSlide}
          onReorder={() => {}}
        />

        {/* Canvas */}
        <SlideCanvas
          elements={currentElements}
          selectedElementIdx={selectedElementIdx}
          onSelectElement={setSelectedElementIdx}
          onUpdateElement={handleUpdateElement}
          aspectRatio={aspectRatio}
          backgroundColor={theme.background}
        />
      </div>

      {/* Speaker notes */}
      <SpeakerNotes notes={currentSlide?.speakerNotes || ""} onChange={handleUpdateNotes} />

      {/* Status bar */}
      <PresStatusBar currentSlide={activeSlide} totalSlides={slides.length} />
    </div>
  );
}
