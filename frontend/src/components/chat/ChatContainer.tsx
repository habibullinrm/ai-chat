'use client';

import { useState, useEffect } from 'react';
import { useChatStore } from '@/stores/chatStore';
import { useSettingsStore } from '@/stores/settingsStore';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { ProviderSelector } from './ProviderSelector';
import type { ChatParameters } from '@/types';

export function ChatContainer() {
  const { currentConversation, isSending, sendMessage, clearConversation, error } = useChatStore();
  const { defaultProvider, defaultModel, defaultParameters } = useSettingsStore();

  // Локальное состояние для выбора провайдера/модели
  const [selectedProvider, setSelectedProvider] = useState(defaultProvider);
  const [selectedModel, setSelectedModel] = useState(defaultModel);
  const [parameters, setParameters] = useState<ChatParameters>(defaultParameters);

  // Синхронизация с текущим диалогом
  useEffect(() => {
    if (currentConversation) {
      setSelectedProvider(currentConversation.provider || defaultProvider);
      setSelectedModel(currentConversation.model || defaultModel);
    } else {
      setSelectedProvider(defaultProvider);
      setSelectedModel(defaultModel);
      setParameters(defaultParameters);
    }
  }, [currentConversation, defaultProvider, defaultModel, defaultParameters]);

  const handleSend = async (message: string) => {
    try {
      await sendMessage({
        conversation_id: currentConversation?.id,
        message,
        provider: selectedProvider,
        model: selectedModel,
        parameters,
      });
    } catch {
      // Ошибка уже в store
    }
  };

  const handleClear = async () => {
    if (currentConversation && confirm('Очистить все сообщения в этом чате?')) {
      await clearConversation(currentConversation.id);
    }
  };

  return (
    <div className="flex flex-col h-full relative">
      {/* Панель управления */}
      <div className="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
        {/* Селектор провайдера */}
        <ProviderSelector
          selectedProvider={selectedProvider}
          selectedModel={selectedModel}
          parameters={parameters}
          onProviderChange={setSelectedProvider}
          onModelChange={setSelectedModel}
          onParametersChange={setParameters}
          disabled={isSending || !!currentConversation}
        />

        {/* Кнопка очистки */}
        {currentConversation && currentConversation.messages.length > 0 && (
          <button
            onClick={handleClear}
            disabled={isSending}
            className="mr-2 p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 disabled:opacity-50"
            title="Очистить чат"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/30 text-red-500 px-4 py-2 text-sm">
          {error}
        </div>
      )}

      <MessageList
        messages={currentConversation?.messages || []}
        isLoading={isSending}
      />

      <ChatInput onSend={handleSend} isLoading={isSending} />
    </div>
  );
}
