import type { FileType } from "./common";

export interface Comment {
  id: string;
  file_type: FileType;
  file_id: string;
  user_id: string;
  content: string;
  position_json: Record<string, unknown> | null;
  parent_comment_id: string | null;
  resolved: boolean;
  resolved_by: string | null;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
  author_name: string | null;
  author_avatar: string | null;
}
