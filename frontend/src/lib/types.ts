// Tipos compartidos con la respuesta del backend (FastAPI).

export interface ChannelResult {
  nombre: string;
  suscriptores: number;
  subs_fmt: string;
  views: number;
  videos: number;
  email: string;
  instagram: string;
  tiktok: string;
  twitter: string;
  facebook: string;
  linkedin: string;
  website: string;
  canal_url: string;
  keyword_origen: string;
  descripcion: string;
}

export interface SearchResponse {
  results: ChannelResult[];
  total: number;
  remaining: number | null;
  used_own_key: boolean;
}

export interface SearchParams {
  keywords: string[];
  min_subs: number;
  max_subs: number;
  language: string;
  user_api_key?: string;
}
