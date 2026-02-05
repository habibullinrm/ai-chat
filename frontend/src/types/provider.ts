// Типы для провайдеров

export interface Model {
  id: string;
  name: string;
  description: string | null;
  max_tokens: number;
  supports_streaming: boolean;
}

export interface Provider {
  id: string;
  name: string;
  description: string | null;
  models: Model[];
  is_available: boolean;
}

export interface ProvidersResponse {
  providers: Provider[];
}
