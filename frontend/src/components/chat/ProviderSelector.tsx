'use client';

import { useEffect, useState } from 'react';
import { useProviderStore } from '@/stores/providerStore';
import { useSettingsStore } from '@/stores/settingsStore';
import type { ChatParameters } from '@/types';

interface ProviderSelectorProps {
  selectedProvider: string;
  selectedModel: string;
  parameters: ChatParameters;
  onProviderChange: (provider: string) => void;
  onModelChange: (model: string) => void;
  onParametersChange: (params: ChatParameters) => void;
  disabled?: boolean;
}

export function ProviderSelector({
  selectedProvider,
  selectedModel,
  parameters,
  onProviderChange,
  onModelChange,
  onParametersChange,
  disabled = false,
}: ProviderSelectorProps) {
  const { providers, isLoading, loadProviders, getModelsForProvider } = useProviderStore();
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    if (providers.length === 0) {
      loadProviders();
    }
  }, [providers.length, loadProviders]);

  const models = getModelsForProvider(selectedProvider);

  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newProvider = e.target.value;
    onProviderChange(newProvider);

    // Автоматически выбираем первую модель нового провайдера
    const newModels = getModelsForProvider(newProvider);
    if (newModels.length > 0) {
      onModelChange(newModels[0].id);
    }
  };

  return (
    <div className="flex items-center gap-2 p-2 flex-1">
      {/* Провайдер */}
      <div className="flex items-center gap-1">
        <label className="text-xs text-gray-500 dark:text-gray-400">Провайдер:</label>
        <select
          value={selectedProvider}
          onChange={handleProviderChange}
          disabled={disabled || isLoading}
          className="text-sm px-2 py-1 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {providers.map((provider) => (
            <option
              key={provider.id}
              value={provider.id}
              disabled={!provider.is_available}
            >
              {provider.name} {!provider.is_available && '(недоступен)'}
            </option>
          ))}
          {providers.length === 0 && !isLoading && (
            <option value={selectedProvider}>{selectedProvider}</option>
          )}
        </select>
      </div>

      {/* Модель */}
      <div className="flex items-center gap-1">
        <label className="text-xs text-gray-500 dark:text-gray-400">Модель:</label>
        <select
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          disabled={disabled || isLoading}
          className="text-sm px-2 py-1 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {models.map((model) => (
            <option key={model.id} value={model.id}>
              {model.name}
            </option>
          ))}
          {models.length === 0 && (
            <option value={selectedModel}>{selectedModel}</option>
          )}
        </select>
      </div>

      {/* Кнопка настроек */}
      <button
        onClick={() => setShowSettings(!showSettings)}
        disabled={disabled}
        className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400"
        title="Параметры генерации"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      </button>

      {/* Панель настроек */}
      {showSettings && (
        <div className="absolute top-full left-0 right-0 mt-1 p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-10">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Temperature */}
            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                Temperature: {parameters.temperature?.toFixed(1)}
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={parameters.temperature || 0.7}
                onChange={(e) =>
                  onParametersChange({ ...parameters, temperature: parseFloat(e.target.value) })
                }
                disabled={disabled}
                className="w-full"
              />
            </div>

            {/* Max Tokens */}
            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                Max Tokens: {parameters.max_tokens}
              </label>
              <input
                type="range"
                min="256"
                max="8192"
                step="256"
                value={parameters.max_tokens || 2048}
                onChange={(e) =>
                  onParametersChange({ ...parameters, max_tokens: parseInt(e.target.value) })
                }
                disabled={disabled}
                className="w-full"
              />
            </div>

            {/* Top P */}
            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                Top P: {parameters.top_p?.toFixed(1)}
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={parameters.top_p || 1.0}
                onChange={(e) =>
                  onParametersChange({ ...parameters, top_p: parseFloat(e.target.value) })
                }
                disabled={disabled}
                className="w-full"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
