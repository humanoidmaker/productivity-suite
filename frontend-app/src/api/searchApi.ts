import { apiFetch } from "./client";

export interface SearchResult {
  type: "document" | "spreadsheet" | "presentation";
  id: string;
  title: string;
  snippet: string;
  updated_at: string;
}

export async function searchFiles(query: string): Promise<{ query: string; results: SearchResult[]; count: number }> {
  return apiFetch(`/search?q=${encodeURIComponent(query)}`);
}
