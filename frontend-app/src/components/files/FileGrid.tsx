import { FileCard } from "./FileCard";
import type { FolderContents } from "@/types/folder";

interface Props {
  contents: FolderContents;
}

export function FileGrid({ contents }: Props) {
  const allItems = [
    ...contents.folders.map(f => ({ id: f.id, title: f.name, type: "folder" as const, updatedAt: f.updated_at })),
    ...contents.documents.map(d => ({ id: d.id, title: d.title, type: "document" as const, updatedAt: d.updated_at })),
    ...contents.spreadsheets.map(s => ({ id: s.id, title: s.title, type: "spreadsheet" as const, updatedAt: s.updated_at })),
    ...contents.presentations.map(p => ({ id: p.id, title: p.title, type: "presentation" as const, updatedAt: p.updated_at })),
  ];

  if (allItems.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-gray-400">
        <div className="text-4xl mb-3">📁</div>
        <p className="text-sm">This folder is empty</p>
        <p className="text-xs mt-1">Click "New" to create a file</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      {allItems.map(item => (
        <FileCard key={`${item.type}-${item.id}`} {...item} />
      ))}
    </div>
  );
}
