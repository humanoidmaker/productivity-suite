import { useNavigate } from "react-router-dom";
import { MoreVertical, Folder } from "lucide-react";
import { FileIcon } from "./FileIcon";
import type { FileType } from "@/types/common";

interface Props {
  id: string;
  title: string;
  type: FileType | "folder";
  updatedAt: string;
  onContextMenu?: (e: React.MouseEvent) => void;
}

export function FileCard({ id, title, type, updatedAt, onContextMenu }: Props) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (type === "folder") navigate(`/files/${id}`);
    else navigate(`/${type}/${id}`);
  };

  const timeAgo = formatTimeAgo(updatedAt);

  return (
    <button
      onClick={handleClick}
      onContextMenu={onContextMenu}
      className="group w-full text-left rounded-xl border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all bg-white overflow-hidden"
    >
      {/* Thumbnail */}
      <div className="h-32 bg-gray-50 flex items-center justify-center border-b border-gray-100">
        {type === "folder" ? (
          <Folder className="h-12 w-12 text-gray-300" />
        ) : (
          <FileIcon type={type} size="lg" />
        )}
      </div>

      {/* Info */}
      <div className="p-3">
        <div className="flex items-center gap-2">
          <FileIcon type={type} size="sm" />
          <h3 className="text-sm font-medium text-gray-900 truncate flex-1">{title}</h3>
          <button
            onClick={e => { e.stopPropagation(); onContextMenu?.(e); }}
            className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-gray-100 transition-opacity"
          >
            <MoreVertical className="h-4 w-4 text-gray-400" />
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-1">{timeAgo}</p>
      </div>
    </button>
  );
}

function formatTimeAgo(dateStr: string): string {
  const d = new Date(dateStr);
  const now = Date.now();
  const diff = now - d.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return d.toLocaleDateString();
}
