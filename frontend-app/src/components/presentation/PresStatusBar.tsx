interface Props {
  currentSlide: number;
  totalSlides: number;
}

export function PresStatusBar({ currentSlide, totalSlides }: Props) {
  return (
    <div className="h-6 bg-gray-50 border-t border-gray-200 flex items-center px-4 text-[10px] text-gray-500 gap-6 shrink-0">
      <span>Slide {currentSlide + 1} of {totalSlides}</span>
      <div className="flex-1" />
      <span>100%</span>
    </div>
  );
}
