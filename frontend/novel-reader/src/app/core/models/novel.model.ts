export interface NovelOut {
  id: number;
  name: string;
  source_lang: string;
  target_lang: string;
  context_json?: any;
  created_at?: string;
  updated_at?: string;
}

export interface NovelCreate {
  name: string;
  source_lang: string;
  target_lang: string;
}
