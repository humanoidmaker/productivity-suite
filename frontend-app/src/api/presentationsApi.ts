import { apiFetch } from "./client";
import type { Presentation } from "@/types/presentation";
import type { PaginatedResponse } from "@/types/common";

export async function createPresentation(data: { title?: string; folder_id?: string; aspect_ratio?: string }): Promise<Presentation> {
  return apiFetch("/presentations", { method: "POST", body: JSON.stringify(data) });
}

export async function listPresentations(page = 1, pageSize = 20): Promise<PaginatedResponse<Presentation>> {
  return apiFetch(`/presentations?page=${page}&page_size=${pageSize}`);
}

export async function getPresentation(id: string): Promise<Presentation> {
  return apiFetch(`/presentations/${id}`);
}

export async function updatePresentation(id: string, data: Record<string, unknown>): Promise<Presentation> {
  return apiFetch(`/presentations/${id}`, { method: "PATCH", body: JSON.stringify(data) });
}

export async function duplicatePresentation(id: string): Promise<Presentation> {
  return apiFetch(`/presentations/${id}/duplicate`, { method: "POST" });
}

export async function deletePresentation(id: string): Promise<void> {
  await apiFetch(`/presentations/${id}`, { method: "DELETE" });
}
