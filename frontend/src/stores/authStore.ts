// Store для авторизации

import { create } from 'zustand';
import { api, loginApi, registerApi } from '@/lib/api';
import { setTokens, clearTokens, isAuthenticated } from '@/lib/auth';
import type { User } from '@/types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const tokens = await loginApi(email, password);
      setTokens(tokens.access_token, tokens.refresh_token);

      const user = await api.get<User>('/api/v1/auth/me');
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (e) {
      set({
        error: e instanceof Error ? e.message : 'Ошибка входа',
        isLoading: false,
      });
      throw e;
    }
  },

  register: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      await registerApi(email, password);
      set({ isLoading: false });
    } catch (e) {
      set({
        error: e instanceof Error ? e.message : 'Ошибка регистрации',
        isLoading: false,
      });
      throw e;
    }
  },

  logout: () => {
    clearTokens();
    set({ user: null, isAuthenticated: false, error: null });
  },

  checkAuth: async () => {
    if (!isAuthenticated()) {
      set({ isLoading: false, isAuthenticated: false });
      return;
    }

    try {
      const user = await api.get<User>('/api/v1/auth/me');
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      clearTokens();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
