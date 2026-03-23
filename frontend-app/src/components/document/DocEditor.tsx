import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import TextAlign from "@tiptap/extension-text-align";
import TextStyle from "@tiptap/extension-text-style";
import Color from "@tiptap/extension-color";
import Highlight from "@tiptap/extension-highlight";
import Link from "@tiptap/extension-link";
import Image from "@tiptap/extension-image";
import Placeholder from "@tiptap/extension-placeholder";
import CharacterCount from "@tiptap/extension-character-count";
import { useEffect, useCallback, useRef } from "react";

interface Props {
  initialContent?: string;
  onUpdate?: (html: string) => void;
  editable?: boolean;
}

export function DocEditor({ initialContent, onUpdate, editable = true }: Props) {
  const onUpdateRef = useRef(onUpdate);
  onUpdateRef.current = onUpdate;

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        history: { depth: 100 },
      }),
      Underline,
      TextAlign.configure({ types: ["heading", "paragraph"] }),
      TextStyle,
      Color,
      Highlight.configure({ multicolor: true }),
      Link.configure({ openOnClick: false, HTMLAttributes: { class: "text-primary-600 underline cursor-pointer" } }),
      Image.configure({ HTMLAttributes: { class: "max-w-full rounded" } }),
      Placeholder.configure({ placeholder: "Start typing..." }),
      CharacterCount,
    ],
    content: initialContent || "",
    editable,
    onUpdate: ({ editor }) => {
      onUpdateRef.current?.(editor.getHTML());
    },
    editorProps: {
      attributes: {
        class: "prose prose-sm max-w-none focus:outline-none min-h-[60vh] px-16 py-12",
      },
    },
  });

  // Update content if initialContent changes (e.g., after load)
  useEffect(() => {
    if (editor && initialContent && !editor.isDestroyed) {
      const current = editor.getHTML();
      if (current !== initialContent && current === "<p></p>") {
        editor.commands.setContent(initialContent, false);
      }
    }
  }, [editor, initialContent]);

  return (
    <div className="flex-1 overflow-auto bg-gray-50">
      <div className="max-w-[850px] mx-auto my-8 bg-white shadow-sm border border-gray-200 rounded-sm min-h-[1100px]">
        <EditorContent editor={editor} />
      </div>
    </div>
  );
}

// Re-export editor hook for toolbar access
export { useEditor };
