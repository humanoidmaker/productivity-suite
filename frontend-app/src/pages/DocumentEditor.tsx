import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import UnderlineExt from "@tiptap/extension-underline";
import TextAlign from "@tiptap/extension-text-align";
import TextStyle from "@tiptap/extension-text-style";
import ColorExt from "@tiptap/extension-color";
import Highlight from "@tiptap/extension-highlight";
import LinkExt from "@tiptap/extension-link";
import ImageExt from "@tiptap/extension-image";
import Placeholder from "@tiptap/extension-placeholder";
import CharacterCount from "@tiptap/extension-character-count";
import { ArrowLeft, Save, Download, Loader2, Check } from "lucide-react";
import { getDocumentContent, updateDocument } from "@/api/documentsApi";
import { DocToolbar } from "@/components/document/DocToolbar";
import { DocStatusBar } from "@/components/document/DocStatusBar";
import type { DocumentContent } from "@/types/document";

export default function DocumentEditor() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [docData, setDocData] = useState<DocumentContent | null>(null);
  const [title, setTitle] = useState("Untitled Document");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);
  const autoSaveTimer = useRef<ReturnType<typeof setTimeout>>();

  const editor = useEditor({
    extensions: [
      StarterKit.configure({ history: { depth: 100 } }),
      UnderlineExt,
      TextAlign.configure({ types: ["heading", "paragraph"] }),
      TextStyle,
      ColorExt,
      Highlight.configure({ multicolor: true }),
      LinkExt.configure({ openOnClick: false }),
      ImageExt,
      Placeholder.configure({ placeholder: "Start typing..." }),
      CharacterCount,
    ],
    content: "",
    editorProps: {
      attributes: {
        class: "prose prose-sm max-w-none focus:outline-none min-h-[80vh] px-16 py-12",
      },
    },
    onUpdate: () => {
      setSaved(false);
      // Debounced auto-save
      clearTimeout(autoSaveTimer.current);
      autoSaveTimer.current = setTimeout(() => handleSave(), 3000);
    },
  });

  // Load document
  useEffect(() => {
    if (!id) return;
    getDocumentContent(id)
      .then(data => {
        setDocData(data);
        setTitle(data.title);
        if (data.content_html && editor && !editor.isDestroyed) {
          editor.commands.setContent(data.content_html, false);
        }
      })
      .catch(() => navigate("/"))
      .finally(() => setLoading(false));
  }, [id, editor, navigate]);

  const handleSave = useCallback(async () => {
    if (!id || !editor) return;
    setSaving(true);
    try {
      await updateDocument(id, { title, content_html: editor.getHTML() });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      // Silent fail on auto-save
    } finally {
      setSaving(false);
    }
  }, [id, editor, title]);

  // Ctrl+S save
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        handleSave();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleSave]);

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Top bar */}
      <div className="h-12 bg-white border-b border-gray-200 flex items-center px-3 gap-3 shrink-0">
        <button onClick={() => navigate("/")} className="p-1.5 rounded hover:bg-gray-100 text-gray-500">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="h-7 w-7 rounded bg-doc/10 flex items-center justify-center">
          <span className="text-doc text-[10px] font-bold">D</span>
        </div>
        <input
          value={title}
          onChange={e => { setTitle(e.target.value); setSaved(false); }}
          onBlur={handleSave}
          className="text-sm font-medium text-gray-900 bg-transparent border-none focus:outline-none focus:bg-gray-50 focus:ring-1 focus:ring-primary-500 rounded px-1 -mx-1 min-w-0 flex-1 max-w-md"
        />
        <div className="flex items-center gap-2 ml-auto">
          {saving && <Loader2 className="h-3.5 w-3.5 animate-spin text-gray-400" />}
          {saved && <Check className="h-3.5 w-3.5 text-green-500" />}
          <button onClick={handleSave} className="flex items-center gap-1 px-3 h-7 text-xs text-gray-600 hover:bg-gray-100 rounded">
            <Save className="h-3 w-3" /> Save
          </button>
          <button
            onClick={() => { if (id) window.open(`/api/v1/documents/${id}/export/docx`, "_blank"); }}
            className="flex items-center gap-1 px-3 h-7 text-xs text-gray-600 hover:bg-gray-100 rounded"
          >
            <Download className="h-3 w-3" /> Export
          </button>
        </div>
      </div>

      {/* Toolbar */}
      <DocToolbar editor={editor} />

      {/* Editor area */}
      <div className="flex-1 overflow-auto bg-gray-100">
        <div className="max-w-[850px] mx-auto my-6 bg-white shadow-sm border border-gray-200 rounded-sm min-h-[1100px]">
          <EditorContent editor={editor} />
        </div>
      </div>

      {/* Status bar */}
      <DocStatusBar editor={editor} />
    </div>
  );
}
