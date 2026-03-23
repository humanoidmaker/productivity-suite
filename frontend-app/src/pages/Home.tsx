import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FileText, Table2, Presentation, Clock, Loader2 } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { createDocument } from "@/api/documentsApi";
import { listFolderContents } from "@/api/foldersApi";
import { FileGrid } from "@/components/files/FileGrid";
import type { FolderContents } from "@/types/folder";

export default function Home() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [contents, setContents] = useState<FolderContents | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listFolderContents()
      .then(setContents)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const quickCreate = async (type: string) => {
    if (type === "document") {
      const doc = await createDocument({});
      navigate(`/document/${doc.id}`);
    }
    // Spreadsheet and presentation will be added in Phase 5
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Welcome */}
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        Welcome back, {user?.name?.split(" ")[0]}
      </h1>

      {/* Quick create */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <button onClick={() => quickCreate("document")} className="flex items-center gap-3 p-4 rounded-xl border-2 border-dashed border-gray-200 hover:border-doc hover:bg-doc/5 transition-colors group">
          <div className="h-10 w-10 rounded-lg bg-doc/10 flex items-center justify-center group-hover:bg-doc/20">
            <FileText className="h-5 w-5 text-doc" />
          </div>
          <div className="text-left">
            <p className="text-sm font-medium text-gray-900">New Document</p>
            <p className="text-xs text-gray-400">Word processor</p>
          </div>
        </button>

        <button onClick={() => quickCreate("spreadsheet")} className="flex items-center gap-3 p-4 rounded-xl border-2 border-dashed border-gray-200 hover:border-sheet hover:bg-sheet/5 transition-colors group">
          <div className="h-10 w-10 rounded-lg bg-sheet/10 flex items-center justify-center group-hover:bg-sheet/20">
            <Table2 className="h-5 w-5 text-sheet" />
          </div>
          <div className="text-left">
            <p className="text-sm font-medium text-gray-900">New Spreadsheet</p>
            <p className="text-xs text-gray-400">Formulas & data</p>
          </div>
        </button>

        <button onClick={() => quickCreate("presentation")} className="flex items-center gap-3 p-4 rounded-xl border-2 border-dashed border-gray-200 hover:border-pres hover:bg-pres/5 transition-colors group">
          <div className="h-10 w-10 rounded-lg bg-pres/10 flex items-center justify-center group-hover:bg-pres/20">
            <Presentation className="h-5 w-5 text-pres" />
          </div>
          <div className="text-left">
            <p className="text-sm font-medium text-gray-900">New Presentation</p>
            <p className="text-xs text-gray-400">Slides & visuals</p>
          </div>
        </button>
      </div>

      {/* Recent files */}
      <div>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Clock className="h-4 w-4" /> Recent Files
        </h2>
        {loading ? (
          <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-gray-400" /></div>
        ) : contents ? (
          <FileGrid contents={contents} />
        ) : (
          <p className="text-sm text-gray-400 text-center py-12">No files yet. Create your first document!</p>
        )}
      </div>
    </div>
  );
}
