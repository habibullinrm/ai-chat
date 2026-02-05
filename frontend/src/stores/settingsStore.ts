// Store для настроек

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ChatParameters } from '@/types';

type Theme = 'light' | 'dark' | 'system';

interface SettingsState {
  theme: Theme;
  defaultProvider: string;
  defaultModel: string;
  defaultParameters: ChatParameters;

  setTheme: (theme: Theme) => void;
  setDefaultProvider: (provider: string) => void;
  setDefaultModel: (model: string) => void;
  setDefaultParameters: (params: Partial<ChatParameters>) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set, get) => ({
      theme: 'system',
      defaultProvider: 'deepseek',
      defaultModel: 'deepseek-chat',
      defaultParameters: {
        temperature: 0.7,
        max_tokens: 2048,
        top_p: 1.0,
      },

      setTheme: (theme) => set({ theme }),
      setDefaultProvider: (defaultProvider) => set({ defaultProvider }),
      setDefaultModel: (defaultModel) => set({ defaultModel }),
      setDefaultParameters: (params) =>
        set({
          defaultParameters: { ...get().defaultParameters, ...params },
        }),
    }),
    {
      name: 'ai-chat-settings',
    }
  )
);
