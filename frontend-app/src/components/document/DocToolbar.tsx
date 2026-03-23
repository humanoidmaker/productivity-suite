import { type Editor } from "@tiptap/react";
import {
  Bold, Italic, Underline, Strikethrough, AlignLeft, AlignCenter, AlignRight, AlignJustify,
  List, ListOrdered, Indent, Outdent, Code, Quote, Minus, Undo2, Redo2, Link, Image,
  Table, Type, Heading1, Heading2, Heading3, Pilcrow, ChevronDown,
} from "lucide-react";
import { useState } from "react";

interface Props {
  editor: Editor | null;
}

export function DocToolbar({ editor }: Props) {
  const [showHeadingMenu, setShowHeadingMenu] = useState(false);

  if (!editor) return null;

  const btn = (active: boolean, onClick: () => void, icon: React.ReactNode, title: string) => (
    <button
      onClick={onClick}
      title={title}
      className={`p-1.5 rounded hover:bg-gray-100 transition-colors ${active ? "bg-primary-100 text-primary-700" : "text-gray-600"}`}
    >
      {icon}
    </button>
  );

  const sep = () => <div className="w-px h-5 bg-gray-200 mx-0.5" />;

  return (
    <div className="flex items-center gap-0.5 px-3 py-1.5 border-b border-gray-200 bg-white flex-wrap">
      {/* Undo/Redo */}
      {btn(false, () => editor.chain().focus().undo().run(), <Undo2 className="h-4 w-4" />, "Undo (Ctrl+Z)")}
      {btn(false, () => editor.chain().focus().redo().run(), <Redo2 className="h-4 w-4" />, "Redo (Ctrl+Y)")}

      {sep()}

      {/* Headings */}
      <div className="relative">
        <button
          onClick={() => setShowHeadingMenu(v => !v)}
          className="flex items-center gap-1 px-2 py-1.5 rounded text-xs text-gray-600 hover:bg-gray-100"
        >
          <Pilcrow className="h-3.5 w-3.5" />
          {editor.isActive("heading", { level: 1 }) ? "Heading 1" :
           editor.isActive("heading", { level: 2 }) ? "Heading 2" :
           editor.isActive("heading", { level: 3 }) ? "Heading 3" : "Normal"}
          <ChevronDown className="h-3 w-3" />
        </button>
        {showHeadingMenu && (
          <div className="absolute left-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-xl py-1 z-50 w-36">
            <button onClick={() => { editor.chain().focus().setParagraph().run(); setShowHeadingMenu(false); }} className="w-full text-left px-3 py-1.5 text-sm hover:bg-gray-50">Normal</button>
            <button onClick={() => { editor.chain().focus().toggleHeading({ level: 1 }).run(); setShowHeadingMenu(false); }} className="w-full text-left px-3 py-1.5 text-lg font-bold hover:bg-gray-50">Heading 1</button>
            <button onClick={() => { editor.chain().focus().toggleHeading({ level: 2 }).run(); setShowHeadingMenu(false); }} className="w-full text-left px-3 py-1.5 text-base font-bold hover:bg-gray-50">Heading 2</button>
            <button onClick={() => { editor.chain().focus().toggleHeading({ level: 3 }).run(); setShowHeadingMenu(false); }} className="w-full text-left px-3 py-1.5 text-sm font-bold hover:bg-gray-50">Heading 3</button>
          </div>
        )}
      </div>

      {sep()}

      {/* Text formatting */}
      {btn(editor.isActive("bold"), () => editor.chain().focus().toggleBold().run(), <Bold className="h-4 w-4" />, "Bold (Ctrl+B)")}
      {btn(editor.isActive("italic"), () => editor.chain().focus().toggleItalic().run(), <Italic className="h-4 w-4" />, "Italic (Ctrl+I)")}
      {btn(editor.isActive("underline"), () => editor.chain().focus().toggleUnderline().run(), <Underline className="h-4 w-4" />, "Underline (Ctrl+U)")}
      {btn(editor.isActive("strike"), () => editor.chain().focus().toggleStrike().run(), <Strikethrough className="h-4 w-4" />, "Strikethrough")}

      {sep()}

      {/* Alignment */}
      {btn(editor.isActive({ textAlign: "left" }), () => editor.chain().focus().setTextAlign("left").run(), <AlignLeft className="h-4 w-4" />, "Align Left")}
      {btn(editor.isActive({ textAlign: "center" }), () => editor.chain().focus().setTextAlign("center").run(), <AlignCenter className="h-4 w-4" />, "Align Center")}
      {btn(editor.isActive({ textAlign: "right" }), () => editor.chain().focus().setTextAlign("right").run(), <AlignRight className="h-4 w-4" />, "Align Right")}
      {btn(editor.isActive({ textAlign: "justify" }), () => editor.chain().focus().setTextAlign("justify").run(), <AlignJustify className="h-4 w-4" />, "Justify")}

      {sep()}

      {/* Lists */}
      {btn(editor.isActive("bulletList"), () => editor.chain().focus().toggleBulletList().run(), <List className="h-4 w-4" />, "Bullet List")}
      {btn(editor.isActive("orderedList"), () => editor.chain().focus().toggleOrderedList().run(), <ListOrdered className="h-4 w-4" />, "Numbered List")}

      {sep()}

      {/* Insert */}
      {btn(editor.isActive("blockquote"), () => editor.chain().focus().toggleBlockquote().run(), <Quote className="h-4 w-4" />, "Blockquote")}
      {btn(editor.isActive("codeBlock"), () => editor.chain().focus().toggleCodeBlock().run(), <Code className="h-4 w-4" />, "Code Block")}
      {btn(false, () => editor.chain().focus().setHorizontalRule().run(), <Minus className="h-4 w-4" />, "Horizontal Rule")}
      {btn(editor.isActive("link"), () => {
        const url = prompt("Enter URL:");
        if (url) editor.chain().focus().setLink({ href: url }).run();
      }, <Link className="h-4 w-4" />, "Insert Link")}
      {btn(false, () => {
        const url = prompt("Enter image URL:");
        if (url) editor.chain().focus().setImage({ src: url }).run();
      }, <Image className="h-4 w-4" />, "Insert Image")}
    </div>
  );
}
