import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

interface Props {
  notes: string;
  onChange: (notes: string) => void;
}

export function SpeakerNotes({ notes, onChange }: Props) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="border-t border-gray-200 bg-white shrink-0">
      <button onClick={() => setExpanded(v => !v)} className="w-full flex items-center justify-between px-4 py-1.5 text-[11px] font-medium text-gray-500 hover:bg-gray-50">
        Speaker Notes
        {expanded ? <ChevronDown className="h-3 w-3" /> : <ChevronUp className="h-3 w-3" />}
      </button>
      {expanded && (
        <textarea
          value={notes}
          onChange={e => onChange(e.target.value)}
          placeholder="Click to add speaker notes..."
          className="w-full h-20 px-4 py-2 text-xs text-gray-600 resize-none border-none outline-none bg-gray-50"
        />
      )}
    </div>
  );
}
