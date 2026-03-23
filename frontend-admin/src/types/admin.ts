export interface DashboardStats {
  total_users: number;
  active_users: number;
  total_documents: number;
  total_spreadsheets: number;
  total_presentations: number;
  total_storage_bytes: number;
  active_collaborations: number;
}

export interface SystemHealth {
  postgres: boolean;
  redis: boolean;
  minio: boolean;
  celery_workers: number;
  websocket_connections: number;
  active_sessions: number;
}

export interface SystemSettings {
  default_storage_quota_mb: number;
  max_file_size_mb: number;
  max_collaborators_per_file: number;
  auto_save_interval_seconds: number;
  version_snapshot_interval_minutes: number;
  max_versions_per_file: number;
  trash_auto_purge_days: number;
  registration_enabled: boolean;
  rate_limit_per_minute: number;
}

export interface AdminUser {
  id: string;
  email: string;
  name: string;
  role: string;
  storage_used: number;
  storage_quota: number;
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
}

export interface ActivityEntry {
  id: string;
  user_id: string | null;
  action: string;
  file_type: string | null;
  file_id: string | null;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
