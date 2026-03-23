export interface Folder {
  id: string;
  name: string;
  owner_id: string;
  parent_folder_id: string | null;
  color: string | null;
  icon: string | null;
  is_trashed: boolean;
  created_at: string;
  updated_at: string;
}

export interface FolderContents {
  folders: Folder[];
  documents: import("./document").Document[];
  spreadsheets: import("./spreadsheet").Spreadsheet[];
  presentations: import("./presentation").Presentation[];
}

export interface BreadcrumbItem {
  id: string;
  name: string;
}
