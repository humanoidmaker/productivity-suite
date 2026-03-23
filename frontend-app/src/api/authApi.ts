import { apiFetch, setTokens, clearTokens } from "./client";
import type { User, TokenResponse, LoginRequest, RegisterRequest } from "@/types/user";

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const res = await apiFetch<TokenResponse>("/auth/login", { method: "POST", body: JSON.stringify(data) });
  setTokens(res.access_token, res.refresh_token);
  return res;
}

export async function register(data: RegisterRequest): Promise<TokenResponse> {
  const res = await apiFetch<TokenResponse>("/auth/register", { method: "POST", body: JSON.stringify(data) });
  setTokens(res.access_token, res.refresh_token);
  return res;
}

export async function getMe(): Promise<User> {
  return apiFetch<User>("/auth/me");
}

export async function updateProfile(data: { name?: string; theme_preference?: string }): Promise<User> {
  return apiFetch<User>("/auth/me", { method: "PATCH", body: JSON.stringify(data) });
}

export async function changePassword(current_password: string, new_password: string): Promise<void> {
  await apiFetch("/auth/change-password", { method: "POST", body: JSON.stringify({ current_password, new_password }) });
}

export function logout() {
  clearTokens();
}
