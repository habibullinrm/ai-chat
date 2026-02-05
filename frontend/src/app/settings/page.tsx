'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/stores/authStore';
import { useSettingsStore } from '@/stores/settingsStore';
import { useProviderStore } from '@/stores/providerStore';
import { Button, Spinner } from '@/components/ui';

export default function SettingsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuthStore();
  const {
    theme,
    defaultProvider,
    defaultModel,
    defaultParameters,
    setTheme,
    setDefaultProvider,
    setDefaultModel,
    setDefaultParameters,
  } = useSettingsStore();
  const { providers, isLoading: providersLoading, loadProviders, getModelsForProvider } = useProviderStore();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (providers.length === 0) {
      loadProviders();
    }
  }, [providers.length, loadProviders]);

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const models = getModelsForProvider(defaultProvider);

  const handleProviderChange = (providerId: string) => {
    setDefaultProvider(providerId);
    const providerModels = getModelsForProvider(providerId);
    if (providerModels.length > 0) {
      setDefaultModel(providerModels[0].id);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="h-14 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex items-center px-4">
        <Link href="/" className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span>Назад</span>
        </Link>
        <h1 className="flex-1 text-center text-lg font-semibold text-gray-900 dark:text-white">
          Настройки
        </h1>
        <div className="w-16" /> {/* Spacer для центрирования */}
      </header>

      <main className="max-w-2xl mx-auto p-4 space-y-6">
        {/* Тема */}
        <section className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Внешний вид
          </h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Тема
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'light', label: 'Светлая', icon: 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z' },
                { value: 'dark', label: 'Тёмная', icon: 'M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z' },
                { value: 'system', label: 'Системная', icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => setTheme(option.value as 'light' | 'dark' | 'system')}
                  className={`flex flex-col items-center p-3 rounded-lg border-2 transition-colors ${
                    theme === option.value
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <svg className="w-6 h-6 mb-1 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={option.icon} />
                  </svg>
                  <span className="text-sm text-gray-700 dark:text-gray-300">{option.label}</span>
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Провайдер по умолчанию */}
        <section className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            LLM по умолчанию
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Провайдер
              </label>
              <select
                value={defaultProvider}
                onChange={(e) => handleProviderChange(e.target.value)}
                disabled={providersLoading}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {providers.map((provider) => (
                  <option key={provider.id} value={provider.id} disabled={!provider.is_available}>
                    {provider.name} {!provider.is_available && '(недоступен)'}
                  </option>
                ))}
                {providers.length === 0 && (
                  <option value={defaultProvider}>{defaultProvider}</option>
                )}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Модель
              </label>
              <select
                value={defaultModel}
                onChange={(e) => setDefaultModel(e.target.value)}
                disabled={providersLoading}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {models.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.name}
                  </option>
                ))}
                {models.length === 0 && (
                  <option value={defaultModel}>{defaultModel}</option>
                )}
              </select>
            </div>
          </div>
        </section>

        {/* Параметры генерации */}
        <section className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Параметры генерации
          </h2>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Temperature
                </label>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {defaultParameters.temperature?.toFixed(1)}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={defaultParameters.temperature || 0.7}
                onChange={(e) => setDefaultParameters({ temperature: parseFloat(e.target.value) })}
                className="w-full"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Контролирует случайность ответов. Низкие значения делают ответы более детерминированными.
              </p>
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Max Tokens
                </label>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {defaultParameters.max_tokens}
                </span>
              </div>
              <input
                type="range"
                min="256"
                max="8192"
                step="256"
                value={defaultParameters.max_tokens || 2048}
                onChange={(e) => setDefaultParameters({ max_tokens: parseInt(e.target.value) })}
                className="w-full"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Максимальное количество токенов в ответе.
              </p>
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Top P
                </label>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {defaultParameters.top_p?.toFixed(1)}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={defaultParameters.top_p || 1.0}
                onChange={(e) => setDefaultParameters({ top_p: parseFloat(e.target.value) })}
                className="w-full"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Nucleus sampling. Альтернатива temperature для контроля разнообразия.
              </p>
            </div>
          </div>
        </section>

        {/* Сброс настроек */}
        <section className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <Button
            variant="ghost"
            className="w-full text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30"
            onClick={() => {
              if (confirm('Сбросить все настройки к значениям по умолчанию?')) {
                setTheme('system');
                setDefaultProvider('deepseek');
                setDefaultModel('deepseek-chat');
                setDefaultParameters({
                  temperature: 0.7,
                  max_tokens: 2048,
                  top_p: 1.0,
                });
              }
            }}
          >
            Сбросить настройки
          </Button>
        </section>
      </main>
    </div>
  );
}
