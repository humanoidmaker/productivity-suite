export interface Spreadsheet {
  id: string;
  title: string;
  owner_id: string;
  folder_id: string | null;
  sheets_meta_json: SheetsMeta | null;
  row_count: number;
  col_count: number;
  is_template: boolean;
  template_category: string | null;
  thumbnail_key: string | null;
  is_trashed: boolean;
  last_edited_by: string | null;
  last_edited_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface SheetsMeta {
  sheets: SheetInfo[];
  cells?: Record<string, Record<string, CellData>>;
}

export interface SheetInfo {
  name: string;
  index: number;
  visible: boolean;
  color: string | null;
}

export interface CellData {
  value: string | number | boolean | null;
  formula?: string;
  format?: CellFormat;
}

export interface CellFormat {
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  fontFamily?: string;
  fontSize?: number;
  textColor?: string;
  backgroundColor?: string;
  textAlign?: "left" | "center" | "right";
  verticalAlign?: "top" | "middle" | "bottom";
  numberFormat?: string;
  wrapText?: boolean;
}
