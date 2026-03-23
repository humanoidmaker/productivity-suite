import { FileText, Table2, Presentation as PresIcon } from "lucide-react";
import type { FileType } from "@/types/common";

const ICON_MAP: Record<FileType | "folder", { icon: typeof FileText; color: string; bg: string }> = {
  document: { icon: FileText, color: "text-doc", bg: "bg-doc/10" },
  spreadsheet: { icon: Table2, color: "text-sheet", bg: "bg-sheet/10" },
  presentation: { icon: PresIcon, color: "text-pres", bg: "bg-pres/10" },
  folder: { icon: FileText, color: "text-gray-500", bg: "bg-gray-100" },
};

interface Props {
  type: FileType | "folder";
  size?: "sm" | "md" | "lg";
}

export function FileIcon({ type, size = "md" }: Props) {
  const { icon: Icon, color, bg } = ICON_MAP[type] || ICON_MAP.document;
  const sizeClasses = { sm: "h-6 w-6", md: "h-10 w-10", lg: "h-14 w-14" };
  const iconSizes = { sm: "h-3 w-3", md: "h-5 w-5", lg: "h-7 w-7" };

  return (
    <div className={`${sizeClasses[size]} rounded-lg ${bg} flex items-center justify-center shrink-0`}>
      <Icon className={`${iconSizes[size]} ${color}`} />
    </div>
  );
}
