import { apiFetch } from "./client";
import type { Document, DocumentContent } from "@/types/document";
import type { PaginatedResponse } from "@/types/common";

export async function createDocument(data: { title?: string; folder_id?: string }): Promise<Document> {
  return apiFetch("/documents", { method: "POST", body: JSON.stringify(data) });
}

export async function listDocuments(page = 1, pageSize = 20, folderId?: string): Promise<PaginatedResponse<Document>> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (folderId) params.set("folder_id", folderId);
  return apiFetch(`/documents?${params}`);
}

export async function getDocument(id: string): Promise<Document> {
  return apiFetch(`/documents/${id}`);
}

export async function getDocumentContent(id: string): Promise<DocumentContent> {
  return apiFetch(`/documents/${id}/content`);
}

export async function updateDocument(id: string, data: { title?: string; folder_id?: string; content_html?: string; page_settings_json?: Record<string, unknown> }): Promise<Document> {
  return apiFetch(`/documents/${id}`, { method: "PATCH", body: JSON.stringify(data) });
}

export async function duplicateDocument(id: string): Promise<Document> {
  return apiFetch(`/documents/${id}/duplicate`, { method: "POST" });
}

export async function deleteDocument(id: string): Promise<void> {
  await apiFetch(`/documents/${id}`, { method: "DELETE" });
}

export function getExportUrl(id: string, format: string): string {
  return `/api/v1/documents/${id}/export/${format}`;
}
