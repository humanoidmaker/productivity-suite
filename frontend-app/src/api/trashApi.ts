import { apiFetch } from "./client";

export async function listTrash() {
  return apiFetch<Record<string, unknown[]>>("/trash");
}

export async function restoreItem(fileType: string, fileId: string) {
  return apiFetch(`/trash/restore/${fileType}/${fileId}`, { method: "POST" });
}

export async function permanentDelete(fileType: string, fileId: string) {
  await apiFetch(`/trash/${fileType}/${fileId}`, { method: "DELETE" });
}

export async function emptyTrash() {
  return apiFetch("/trash", { method: "DELETE" });
}
