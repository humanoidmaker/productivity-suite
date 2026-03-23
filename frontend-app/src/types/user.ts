import type { Role } from "./common";

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  role: Role;
  storage_used: number;
  storage_quota: number;
  theme_preference: "light" | "dark" | "system";
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  name: string;
  password: string;
}
