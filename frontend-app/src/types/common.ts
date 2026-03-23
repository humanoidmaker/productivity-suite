export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface MessageResponse {
  message: string;
}

export interface IdResponse {
  id: string;
}

export type FileType = "document" | "spreadsheet" | "presentation";
export type Permission = "view" | "comment" | "edit" | "owner";
export type Role = "user" | "admin" | "superadmin";
