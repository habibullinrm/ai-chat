'use client';

import { useEffect } from 'react';
import { useChatStore } from '@/stores/chatStore';
import { useAuthStore } from '@/stores/authStore';
import { useUIStore } from '@/stores/uiStore';
import { Button, Spinner } from '@/components/ui';
import { ConversationList } from '@/components/sidebar/ConversationList';

export function Sidebar() {
  const { isAuthenticated } = useAuthStore();
  const {
    conversations,
    currentConversation,
    isLoading,
    loadConversations,
    createConversation,
    selectConversation,
    deleteConversation,
  } = useChatStore();
  const { isSidebarOpen, closeSidebar } = useUIStore();

  useEffect(() => {
    if (isAuthenticated) {
      loadConversations();
    }
  }, [isAuthenticated, loadConversations]);

  const handleSelectConversation = (id: string) => {
    selectConversation(id);
    closeSidebar();
  };

  const handleCreateConversation = () => {
    createConversation();
    closeSidebar();
  };

  if (!isAuthenticated) {
    return (
      <aside className="hidden md:flex w-64 border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 p-4">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Войдите, чтобы увидеть историю чатов
        </p>
      </aside>
    );
  }

  return (
    <>
      {/* Overlay для мобильных */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={closeSidebar}
        />
      )}

      <aside
        className={`
          fixed md:relative inset-y-0 left-0 z-50
          w-64 border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 flex flex-col
          transform transition-transform duration-300 ease-in-out
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0 md:transform-none
        `}
      >
        <div className="p-3 flex items-center justify-between">
          <Button
            className="flex-1"
            onClick={handleCreateConversation}
          >
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Новый чат
          </Button>

          {/* Кнопка закрытия для мобильных */}
          <button
            onClick={closeSidebar}
            className="md:hidden ml-2 p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700"
            aria-label="Закрыть меню"
          >
            <svg
              className="w-5 h-5 text-gray-600 dark:text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex justify-center p-4">
              <Spinner size="sm" />
            </div>
          ) : (
            <ConversationList
              conversations={conversations}
              currentId={currentConversation?.id}
              onSelect={handleSelectConversation}
              onDelete={deleteConversation}
            />
          )}
        </div>
      </aside>
    </>
  );
}
