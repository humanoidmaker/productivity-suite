export interface Presentation {
  id: string;
  title: string;
  owner_id: string;
  folder_id: string | null;
  slides_meta_json: SlidesMeta | null;
  slide_count: number;
  theme_json: PresentationTheme | null;
  aspect_ratio: "16:9" | "4:3";
  is_template: boolean;
  template_category: string | null;
  thumbnail_key: string | null;
  is_trashed: boolean;
  last_edited_by: string | null;
  last_edited_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface SlidesMeta {
  slides: SlideInfo[];
  elements: Record<string, SlideElement[]>;
}

export interface SlideInfo {
  id: string;
  layout: string;
  transition: string;
  transitionDuration: number;
  speakerNotes: string;
  hidden: boolean;
}

export interface SlideElement {
  type: "textbox" | "shape" | "image" | "table" | "chart";
  x: number;
  y: number;
  width: number;
  height: number;
  rotation?: number;
  text?: string;
  fontSize?: number;
  bold?: boolean;
  italic?: boolean;
  color?: string;
  textAlign?: string;
  shape?: string;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  src?: string;
  opacity?: number;
}

export interface PresentationTheme {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  text: string;
  headingFont: string;
  bodyFont: string;
}
