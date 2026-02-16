export interface ChapterListItem {
  id: number;
  novel_id: number;
  chapter_no: number;
  title: string | null;
  status: string;
  translated_at: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface ChapterOut extends ChapterListItem {
  raw: string | null;
  content: string | null;
  source_url: string | null;
  prev_chapter_id: number | null;
  next_chapter_id: number | null;
}
