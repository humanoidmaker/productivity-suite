import { apiFetch } from "./client";
import type { Spreadsheet } from "@/types/spreadsheet";
import type { PaginatedResponse } from "@/types/common";

export async function createSpreadsheet(data: { title?: string; folder_id?: string }): Promise<Spreadsheet> {
  return apiFetch("/spreadsheets", { method: "POST", body: JSON.stringify(data) });
}

export async function listSpreadsheets(page = 1, pageSize = 20): Promise<PaginatedResponse<Spreadsheet>> {
  return apiFetch(`/spreadsheets?page=${page}&page_size=${pageSize}`);
}

export async function getSpreadsheet(id: string): Promise<Spreadsheet> {
  return apiFetch(`/spreadsheets/${id}`);
}

export async function updateSpreadsheet(id: string, data: { title?: string; sheets_meta_json?: Record<string, unknown> }): Promise<Spreadsheet> {
  return apiFetch(`/spreadsheets/${id}`, { method: "PATCH", body: JSON.stringify(data) });
}

export async function duplicateSpreadsheet(id: string): Promise<Spreadsheet> {
  return apiFetch(`/spreadsheets/${id}/duplicate`, { method: "POST" });
}

export async function deleteSpreadsheet(id: string): Promise<void> {
  await apiFetch(`/spreadsheets/${id}`, { method: "DELETE" });
}
