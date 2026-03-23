import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { ChevronRight, Loader2 } from "lucide-react";
import { listFolderContents, getBreadcrumb } from "@/api/foldersApi";
import { FileGrid } from "@/components/files/FileGrid";
import type { FolderContents, BreadcrumbItem } from "@/types/folder";
import { Link } from "react-router-dom";

export default function MyFiles() {
  const { folderId } = useParams();
  const [contents, setContents] = useState<FolderContents | null>(null);
  const [breadcrumb, setBreadcrumb] = useState<BreadcrumbItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      listFolderContents(folderId),
      folderId ? getBreadcrumb(folderId) : Promise.resolve([]),
    ])
      .then(([c, b]) => { setContents(c); setBreadcrumb(b); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [folderId]);

  return (
    <div className="p-6">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1 text-sm mb-6">
        <Link to="/files" className="text-gray-500 hover:text-gray-900 font-medium">My Files</Link>
        {breadcrumb.map(item => (
          <span key={item.id} className="flex items-center gap-1">
            <ChevronRight className="h-3.5 w-3.5 text-gray-300" />
            <Link to={`/files/${item.id}`} className="text-gray-500 hover:text-gray-900 font-medium">
              {item.name}
            </Link>
          </span>
        ))}
      </nav>

      {/* Files */}
      {loading ? (
        <div className="flex justify-center py-20"><Loader2 className="h-6 w-6 animate-spin text-gray-400" /></div>
      ) : contents ? (
        <FileGrid contents={contents} />
      ) : null}
    </div>
  );
}
