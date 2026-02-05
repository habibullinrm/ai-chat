// Общие типы для API

export interface ApiError {
  detail: string;
  code?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
