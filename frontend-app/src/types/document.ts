export interface Document {
  id: string;
  title: string;
  owner_id: string;
  folder_id: string | null;
  word_count: number;
  char_count: number;
  page_settings_json: PageSettings | null;
  is_template: boolean;
  template_category: string | null;
  thumbnail_key: string | null;
  is_trashed: boolean;
  last_edited_by: string | null;
  last_edited_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentContent {
  id: string;
  title: string;
  content_html: string | null;
  content_yjs_base64: string | null;
  page_settings_json: PageSettings | null;
}

export interface PageSettings {
  size: "A4" | "Letter" | "Legal";
  orientation: "portrait" | "landscape";
  margins: { top: number; bottom: number; left: number; right: number };
}
