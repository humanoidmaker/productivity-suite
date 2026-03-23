import type { DashboardStats, SystemHealth, SystemSettings, AdminUser, ActivityEntry, PaginatedResponse } from "@/types/admin";

const API_BASE = "/api/v1";

function getToken(): string | null {
  return localStorage.getItem("productivity_access_token");
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = { ...(options.headers as Record<string, string> || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) headers["Content-Type"] = "application/json";

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Auth
export async function adminLogin(email: string, password: string) {
  const res = await apiFetch<{ access_token: string; refresh_token: string }>("/auth/login", {
    method: "POST", body: JSON.stringify({ email, password }),
  });
  localStorage.setItem("productivity_access_token", res.access_token);
  localStorage.setItem("productivity_refresh_token", res.refresh_token);
  return res;
}

export async function getMe() {
  return apiFetch<AdminUser>("/auth/me");
}

// Dashboard
export async function getDashboardStats(): Promise<DashboardStats> {
  return apiFetch("/admin/dashboard");
}

// Users
export async function listUsers(page = 1, pageSize = 20, search?: string): Promise<PaginatedResponse<AdminUser>> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (search) params.set("search", search);
  return apiFetch(`/admin/users?${params}`);
}

export async function createUser(data: { email: string; name: string; password: string; role?: string }) {
  return apiFetch<AdminUser>("/admin/users", { method: "POST", body: JSON.stringify(data) });
}

export async function updateUser(id: string, data: { name?: string; role?: string; is_active?: boolean; storage_quota?: number }) {
  return apiFetch<AdminUser>(`/admin/users/${id}`, { method: "PATCH", body: JSON.stringify(data) });
}

export async function resetPassword(id: string, newPassword: string) {
  return apiFetch(`/admin/users/${id}/reset-password?new_password=${encodeURIComponent(newPassword)}`, { method: "POST" });
}

// System
export async function getSystemHealth(): Promise<SystemHealth> {
  return apiFetch("/admin/system/health");
}

// Settings
export async function getSettings(): Promise<SystemSettings> {
  return apiFetch("/admin/settings");
}

// Activity
export async function getActivityLog(offset = 0, limit = 50): Promise<ActivityEntry[]> {
  return apiFetch(`/admin/activity?offset=${offset}&limit=${limit}`);
}
