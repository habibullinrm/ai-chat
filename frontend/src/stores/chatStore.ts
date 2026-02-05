// Store для чата

import { create } from 'zustand';
import { api } from '@/lib/api';
import type {
  Conversation,
  ConversationWithMessages,
  Message,
  ChatRequest,
  ChatResponse,
  PaginatedResponse,
} from '@/types';

interface ChatState {
  conversations: Conversation[];
  currentConversation: ConversationWithMessages | null;
  isLoading: boolean;
  isSending: boolean;
  error: string | null;

  loadConversations: () => Promise<void>;
  selectConversation: (id: string) => Promise<void>;
  sendMessage: (request: ChatRequest) => Promise<ChatResponse>;
  createConversation: () => void;
  deleteConversation: (id: string) => Promise<void>;
  clearConversation: (id: string) => Promise<void>;
  clearError: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  currentConversation: null,
  isLoading: false,
  isSending: false,
  error: null,

  loadConversations: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get<PaginatedResponse<Conversation>>(
        '/api/v1/conversations?per_page=50'
      );
      set({ conversations: response.items, isLoading: false });
    } catch (e) {
      set({
        error: e instanceof Error ? e.message : 'Ошибка загрузки',
        isLoading: false,
      });
    }
  },

  selectConversation: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const conversation = await api.get<ConversationWithMessages>(
        `/api/v1/conversations/${id}`
      );
      set({ currentConversation: conversation, isLoading: false });
    } catch (e) {
      set({
        error: e instanceof Error ? e.message : 'Ошибка загрузки диалога',
        isLoading: false,
      });
    }
  },

  sendMessage: async (request: ChatRequest) => {
    set({ isSending: true, error: null });

    // Оптимистичное обновление - добавляем сообщение пользователя
    const currentConv = get().currentConversation;
    if (currentConv) {
      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        conversation_id: currentConv.id,
        role: 'user',
        content: request.message,
        tokens_used: null,
        created_at: new Date().toISOString(),
      };
      set({
        currentConversation: {
          ...currentConv,
          messages: [...currentConv.messages, userMessage],
        },
      });
    }

    try {
      const response = await api.post<ChatResponse>(
        '/api/v1/chat/completions',
        request
      );

      // Обновляем диалог с реальными данными
      const { currentConversation, conversations } = get();

      // Создаём сообщение ассистента
      const assistantMessage: Message = {
        id: response.message_id,
        conversation_id: response.conversation_id,
        role: 'assistant',
        content: response.content,
        tokens_used: response.usage.total_tokens,
        created_at: response.created_at,
      };

      if (currentConversation) {
        // Обновляем текущий диалог
        const updatedMessages = currentConversation.messages
          .filter((m) => !m.id.startsWith('temp-'))
          .concat([
            {
              id: `user-${Date.now()}`,
              conversation_id: response.conversation_id,
              role: 'user' as const,
              content: request.message,
              tokens_used: null,
              created_at: new Date().toISOString(),
            },
            assistantMessage,
          ]);

        set({
          currentConversation: {
            ...currentConversation,
            messages: updatedMessages,
          },
          isSending: false,
        });
      } else {
        // Новый диалог - загружаем его
        const newConversation = await api.get<ConversationWithMessages>(
          `/api/v1/conversations/${response.conversation_id}`
        );
        set({
          currentConversation: newConversation,
          conversations: [
            { ...newConversation, messages: undefined } as Conversation,
            ...conversations,
          ],
          isSending: false,
        });
      }

      return response;
    } catch (e) {
      // Откатываем оптимистичное обновление
      if (currentConv) {
        set({
          currentConversation: currentConv,
          error: e instanceof Error ? e.message : 'Ошибка отправки',
          isSending: false,
        });
      } else {
        set({
          error: e instanceof Error ? e.message : 'Ошибка отправки',
          isSending: false,
        });
      }
      throw e;
    }
  },

  createConversation: () => {
    set({ currentConversation: null });
  },

  deleteConversation: async (id: string) => {
    try {
      await api.delete(`/api/v1/conversations/${id}`);
      const { conversations, currentConversation } = get();
      set({
        conversations: conversations.filter((c) => c.id !== id),
        currentConversation:
          currentConversation?.id === id ? null : currentConversation,
      });
    } catch (e) {
      set({
        error: e instanceof Error ? e.message : 'Ошибка удаления',
      });
    }
  },

  clearConversation: async (id: string) => {
    try {
      await api.delete(`/api/v1/conversations/${id}/messages`);
      const { currentConversation } = get();
      if (currentConversation?.id === id) {
        set({
          currentConversation: {
            ...currentConversation,
            messages: [],
          },
        });
      }
    } catch (e) {
      set({
        error: e instanceof Error ? e.message : 'Ошибка очистки',
      });
    }
  },

  clearError: () => set({ error: null }),
}));
