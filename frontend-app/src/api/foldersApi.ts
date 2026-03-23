import { apiFetch } from "./client";
import type { Folder, FolderContents, BreadcrumbItem } from "@/types/folder";

export async function createFolder(data: { name: string; parent_folder_id?: string; color?: string }): Promise<Folder> {
  return apiFetch("/folders", { method: "POST", body: JSON.stringify(data) });
}

export async function getFolder(id: string): Promise<Folder> {
  return apiFetch(`/folders/${id}`);
}

export async function updateFolder(id: string, data: { name?: string; color?: string }): Promise<Folder> {
  return apiFetch(`/folders/${id}`, { method: "PATCH", body: JSON.stringify(data) });
}

export async function moveFolder(id: string, parentId: string | null): Promise<Folder> {
  return apiFetch(`/folders/${id}/move`, { method: "POST", body: JSON.stringify({ parent_folder_id: parentId }) });
}

export async function deleteFolder(id: string): Promise<void> {
  await apiFetch(`/folders/${id}`, { method: "DELETE" });
}

export async function listFolderContents(folderId?: string): Promise<FolderContents> {
  const path = folderId ? `/folders/${folderId}/contents` : "/folders";
  return apiFetch(path);
}

export async function getBreadcrumb(folderId: string): Promise<BreadcrumbItem[]> {
  return apiFetch(`/folders/${folderId}/breadcrumb`);
}

export async function getFolderTree(): Promise<Array<{ id: string; name: string; parent_folder_id: string | null }>> {
  return apiFetch("/folders/tree/all");
}
