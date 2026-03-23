import type { Editor } from "@tiptap/react";

interface Props {
  editor: Editor | null;
}

export function DocStatusBar({ editor }: Props) {
  if (!editor) return null;

  const chars = editor.storage.characterCount?.characters() ?? 0;
  const words = editor.storage.characterCount?.words() ?? 0;

  return (
    <div className="h-7 bg-gray-50 border-t border-gray-200 flex items-center px-4 text-[11px] text-gray-500 gap-4 shrink-0">
      <span>{words} words</span>
      <span>{chars} characters</span>
      <div className="flex-1" />
      <span>100%</span>
    </div>
  );
}
