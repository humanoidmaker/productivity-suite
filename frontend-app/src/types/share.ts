import type { FileType, Permission } from "./common";

export interface Share {
  id: string;
  file_type: FileType;
  file_id: string;
  shared_by: string;
  shared_with_user_id: string | null;
  shared_with_email: string | null;
  share_token: string | null;
  permission: Permission;
  expires_at: string | null;
  created_at: string;
}
