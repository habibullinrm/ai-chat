// Store для провайдеров

import { create } from 'zustand';
import { api } from '@/lib/api';
import type { Provider, ProvidersResponse } from '@/types';

interface ProviderState {
  providers: Provider[];
  isLoading: boolean;
  error: string | null;

  loadProviders: () => Promise<void>;
  getModelsForProvider: (providerId: string) => Provider['models'];
}

export const useProviderStore = create<ProviderState>((set, get) => ({
  providers: [],
  isLoading: false,
  error: null,

  loadProviders: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get<ProvidersResponse>('/api/v1/providers');
      set({ providers: response.providers, isLoading: false });
    } catch (e) {
      set({
        error: e instanceof Error ? e.message : 'Ошибка загрузки провайдеров',
        isLoading: false,
      });
    }
  },

  getModelsForProvider: (providerId: string) => {
    const provider = get().providers.find((p) => p.id === providerId);
    return provider?.models || [];
  },
}));
