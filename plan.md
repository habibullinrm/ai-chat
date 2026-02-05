# План разработки AI-Chat

## Обзор проекта

**AI-Chat** — веб-приложение для асинхронного общения с LLM с поддержкой нескольких провайдеров и middleware pipeline.

| Компонент | Технологии |
|-----------|------------|
| Frontend | Next.js 14+, TypeScript, Tailwind CSS, Zustand, Zod |
| Backend | Python 3.11+, FastAPI, SQLAlchemy (async), Pydantic |
| БД | PostgreSQL, Redis |
| Инфраструктура | Docker, Docker Compose |
| LLM | DeepSeek, OpenAI, Anthropic |

---

## Этапы разработки

### Этап 1: Инфраструктура
Настройка Docker-окружения, структуры проекта, конфигурации контейнеров (PostgreSQL, Redis, backend, frontend).

**Результат:** `docker-compose up` запускает все сервисы

#### Задачи:

**1.1 Структура проекта**
- [ ] Создать корневые директории: `backend/`, `frontend/`
- [ ] Создать `.env.example` с переменными окружения
- [ ] Создать `.gitignore`
- [ ] Создать `README.md` с инструкцией запуска

**1.2 Docker Compose**
- [ ] Создать `docker-compose.yml` с сервисами:
  - `db` — PostgreSQL 15
  - `redis` — Redis 7
  - `backend` — FastAPI приложение
  - `frontend` — Next.js приложение
- [ ] Настроить volumes для персистентности данных
- [ ] Настроить networks для связи сервисов
- [ ] Настроить healthchecks

**1.3 Backend инициализация**
- [ ] Создать `backend/Dockerfile` (Python 3.11)
- [ ] Создать `backend/requirements.txt` с зависимостями:
  - fastapi, uvicorn, pydantic
  - sqlalchemy, asyncpg, alembic
  - python-jose, passlib, bcrypt
  - httpx, redis
- [ ] Создать базовую структуру `backend/app/`:
  - `__init__.py`, `main.py`, `config.py`
- [ ] Настроить CORS и базовый health endpoint

**1.4 Frontend инициализация**
- [ ] Создать Next.js проект с TypeScript (`frontend/`)
- [ ] Создать `frontend/Dockerfile` (Node 20)
- [ ] Установить зависимости: Tailwind CSS, Zod
- [ ] Настроить `tailwind.config.ts`
- [ ] Настроить `next.config.js` с rewrites для проксирования `/api/*` → backend
- [ ] Создать базовую страницу `/`

**1.5 Проверка**
- [ ] `docker-compose up` запускает все контейнеры
- [ ] Backend отвечает на `GET /api/health`
- [ ] Frontend открывается на `http://localhost:3000`
- [ ] PostgreSQL и Redis доступны из backend

---

### Этап 2: Backend — базовый API
Инициализация FastAPI, подключение к БД, модели данных, JWT-аутентификация, базовые CRUD операции, система ролей.

**Результат:** Работающая авторизация и базовые эндпоинты

#### Задачи:

**2.1 Конфигурация приложения**
- [ ] Создать `app/config.py` с настройками через pydantic-settings
- [ ] Настроить загрузку переменных из `.env`
- [ ] Определить настройки: DATABASE_URL, REDIS_URL, SECRET_KEY, токены

**2.2 База данных**
- [ ] Создать `app/db/session.py` — async engine и sessionmaker
- [ ] Создать `app/db/base.py` — базовый класс моделей
- [ ] Инициализировать Alembic для миграций
- [ ] Создать первую миграцию

**2.3 Модели данных**
- [ ] Создать `app/models/user.py`:
  - id, email, hashed_password, role, created_at, updated_at
- [ ] Создать `app/models/conversation.py`:
  - id, user_id, title, provider, model, created_at, updated_at
- [ ] Создать `app/models/message.py`:
  - id, conversation_id, role, content, tokens_used, created_at

**2.4 Pydantic схемы**
- [ ] Создать `app/schemas/user.py`:
  - UserCreate, UserLogin, UserResponse, UserUpdate
- [ ] Создать `app/schemas/token.py`:
  - Token, TokenPayload
- [ ] Создать `app/schemas/common.py`:
  - PaginatedResponse, ErrorResponse

**2.5 Аутентификация**
- [ ] Создать `app/core/security.py`:
  - Хеширование паролей (bcrypt)
  - Создание/верификация JWT токенов
  - Access + Refresh токены
- [ ] Создать `app/api/deps.py`:
  - get_db — dependency для сессии
  - get_current_user — dependency для авторизации
  - require_role — проверка роли

**2.6 API эндпоинты аутентификации**
- [ ] Создать `app/api/v1/auth.py`:
  - POST `/api/auth/register` — регистрация
  - POST `/api/auth/login` — авторизация
  - POST `/api/auth/logout` — выход
  - POST `/api/auth/refresh` — обновление токена
  - GET `/api/auth/me` — текущий пользователь

**2.7 Сервисы**
- [ ] Создать `app/services/auth.py`:
  - create_user, authenticate_user, get_user_by_email
- [ ] Создать `app/services/user.py`:
  - get_user, update_user, delete_user

**2.8 Система ролей**
- [ ] Определить enum Role: guest, user, admin
- [ ] Реализовать проверку ролей в dependencies
- [ ] Добавить rate limiting по ролям (Redis)

**2.9 Обработка ошибок**
- [ ] Создать `app/core/exceptions.py` — кастомные исключения
- [ ] Настроить exception handlers в FastAPI
- [ ] Стандартизировать формат ошибок

**2.10 Проверка**
- [ ] Регистрация нового пользователя работает
- [ ] Логин возвращает access + refresh токены
- [ ] Защищённые эндпоинты требуют авторизации
- [ ] Refresh токен обновляет access токен

---

### Этап 3: Интеграция DeepSeek
Абстракция провайдеров, реализация DeepSeek клиента, эндпоинты чата и диалогов, сохранение истории.

**Результат:** Отправка сообщения → получение ответа от DeepSeek

#### Задачи:

**3.1 Абстракция провайдеров**
- [ ] Создать `app/providers/base.py`:
  - Абстрактный класс `BaseLLMProvider`
  - Метод `chat_completion(messages, params) -> Response`
  - Метод `chat_completion_stream(messages, params) -> AsyncGenerator`
  - Метод `get_models() -> list[Model]`
- [ ] Определить схемы `app/schemas/provider.py`:
  - ProviderInfo, ModelInfo, ChatMessage, ChatResponse, Usage

**3.2 DeepSeek провайдер**
- [ ] Создать `app/providers/deepseek.py`:
  - Реализовать `DeepSeekProvider(BaseLLMProvider)`
  - Подключение к DeepSeek API через httpx
  - Маппинг параметров (temperature, max_tokens, top_p)
  - Парсинг ответа и usage
- [ ] Обработка ошибок API (rate limit, auth, timeout)
- [ ] Retry логика при временных ошибках

**3.3 Реестр провайдеров**
- [ ] Создать `app/providers/__init__.py`:
  - Словарь доступных провайдеров
  - Функция `get_provider(provider_id) -> BaseLLMProvider`
  - Функция `list_providers() -> list[ProviderInfo]`

**3.4 Схемы чата**
- [ ] Создать `app/schemas/chat.py`:
  - ChatCompletionRequest (message, conversation_id, provider, model, parameters)
  - ChatCompletionResponse (id, content, usage, finish_reason)
  - ChatParameters (temperature, max_tokens, top_p, etc.)

**3.5 Сервис чата**
- [ ] Создать `app/services/chat.py`:
  - `send_message(user, request) -> ChatCompletionResponse`
  - Загрузка истории диалога для контекста
  - Вызов провайдера
  - Сохранение сообщения и ответа в БД

**3.6 Сервис диалогов**
- [ ] Создать `app/services/conversation.py`:
  - `create_conversation(user, title, provider, model)`
  - `get_conversations(user, pagination)`
  - `get_conversation(user, conversation_id)`
  - `get_messages(conversation_id, pagination)`
  - `delete_conversation(user, conversation_id)`
  - `update_conversation(user, conversation_id, data)`

**3.7 API эндпоинты чата**
- [ ] Создать `app/api/v1/chat.py`:
  - POST `/api/chat/completions` — отправка сообщения

**3.8 API эндпоинты диалогов**
- [ ] Создать `app/api/v1/conversations.py`:
  - GET `/api/conversations` — список диалогов
  - POST `/api/conversations` — создать диалог
  - GET `/api/conversations/{id}` — получить диалог
  - PATCH `/api/conversations/{id}` — обновить диалог
  - DELETE `/api/conversations/{id}` — удалить диалог
  - GET `/api/conversations/{id}/messages` — сообщения диалога

**3.9 API эндпоинты провайдеров**
- [ ] Создать `app/api/v1/providers.py`:
  - GET `/api/providers` — список провайдеров
  - GET `/api/providers/{id}` — информация о провайдере
  - GET `/api/providers/{id}/models` — модели провайдера
  - GET `/api/providers/{id}/status` — статус доступности

**3.10 Проверка**
- [ ] Отправка сообщения возвращает ответ от DeepSeek
- [ ] История сообщений сохраняется в БД
- [ ] Контекст диалога передаётся в LLM
- [ ] Список провайдеров и моделей возвращается корректно

---

### Этап 4: Middleware система
Абстракция middleware, pipeline обработки, встроенные middleware (фильтр, логгер, system prompt), API управления.

**Результат:** Сообщения проходят через настраиваемый конвейер обработки

#### Задачи:

**4.1 Абстракция middleware**
- [ ] Создать `app/middleware/base.py`:
  - Абстрактный класс `BaseMiddleware`
  - Метод `pre_process(context) -> context` — до LLM
  - Метод `post_process(context, response) -> response` — после LLM
  - Конфигурация через dict
- [ ] Определить `MiddlewareContext`:
  - user, message, conversation, parameters, metadata

**4.2 Pipeline обработки**
- [ ] Создать `app/middleware/pipeline.py`:
  - Класс `MiddlewarePipeline`
  - Загрузка активных middleware из БД
  - Метод `run_pre_process(context)` — цепочка pre
  - Метод `run_post_process(context, response)` — цепочка post
  - Обработка ошибок в цепочке (continue/stop)

**4.3 Модель Middleware в БД**
- [ ] Создать `app/models/middleware.py`:
  - id, name, type (pre/post), description
  - is_active, order, config (JSON)
  - created_at, updated_at
- [ ] Создать миграцию
- [ ] Создать `app/schemas/middleware.py`:
  - MiddlewareCreate, MiddlewareUpdate, MiddlewareResponse

**4.4 Встроенные middleware**
- [ ] Создать `app/middleware/builtin/logger.py`:
  - Логирование входящих сообщений и ответов
  - Конфиг: log_level, include_content
- [ ] Создать `app/middleware/builtin/system_prompt.py`:
  - Добавление системного промпта к запросу
  - Конфиг: prompt_template
- [ ] Создать `app/middleware/builtin/content_filter.py`:
  - Фильтрация по ключевым словам
  - Конфиг: blocked_words, action (block/warn/modify)

**4.5 Реестр middleware**
- [ ] Создать `app/middleware/__init__.py`:
  - Словарь встроенных middleware
  - Функция `get_middleware_class(name)`
  - Функция `create_middleware_instance(config)`

**4.6 Сервис middleware**
- [ ] Создать `app/services/middleware.py`:
  - `get_active_middleware() -> list`
  - `create_middleware(data)`
  - `update_middleware(id, data)`
  - `delete_middleware(id)`
  - `toggle_middleware(id, is_active)`
  - `reorder_middleware(ids_order)`

**4.7 API эндпоинты middleware**
- [ ] Создать `app/api/v1/middleware.py`:
  - GET `/api/middleware` — список всех (admin)
  - GET `/api/middleware/active` — активные (user)
  - POST `/api/middleware` — создать (admin)
  - GET `/api/middleware/{id}` — получить (admin)
  - PUT `/api/middleware/{id}` — обновить (admin)
  - DELETE `/api/middleware/{id}` — удалить (admin)
  - PATCH `/api/middleware/{id}/toggle` — вкл/выкл (admin)
  - PUT `/api/middleware/order` — изменить порядок (admin)

**4.8 Интеграция в chat service**
- [ ] Инициализировать pipeline в chat service
- [ ] Вызывать `pre_process` перед отправкой в LLM
- [ ] Вызывать `post_process` после получения ответа
- [ ] Обрабатывать блокировку сообщения middleware

**4.9 Проверка**
- [ ] Middleware загружаются из БД в правильном порядке
- [ ] Pre-process модифицирует запрос
- [ ] Post-process модифицирует ответ
- [ ] Content filter блокирует запрещённые слова
- [ ] Logger записывает в лог

---

### Этап 5: Frontend
UI компоненты, страницы авторизации, интерфейс чата, sidebar с историей, страница настроек.

**Результат:** Полнофункциональный интерфейс (без streaming)

#### Задачи:

**5.1 API клиент**
- [ ] Создать `src/lib/api.ts`:
  - Базовый fetch/axios клиент
  - Interceptor для добавления Authorization header
  - Interceptor для refresh токена при 401
  - Обработка ошибок API
- [ ] Создать `src/lib/auth.ts`:
  - Хранение токенов (localStorage/cookies)
  - Функции login, logout, refreshToken

**5.2 Типы**
- [ ] Создать `src/types/user.ts`: User, LoginRequest, RegisterRequest
- [ ] Создать `src/types/chat.ts`: Message, Conversation, ChatRequest, ChatResponse
- [ ] Создать `src/types/provider.ts`: Provider, Model
- [ ] Создать `src/types/api.ts`: ApiError, PaginatedResponse

**5.3 Stores (Zustand)**
- [ ] Создать `src/stores/authStore.ts`:
  - user, isAuthenticated, isLoading
  - login(), logout(), checkAuth()
- [ ] Создать `src/stores/chatStore.ts`:
  - conversations, currentConversation, messages
  - sendMessage(), loadConversations(), selectConversation()
- [ ] Создать `src/stores/settingsStore.ts`:
  - theme, defaultProvider, defaultModel, parameters
  - updateSettings()

**5.4 UI компоненты**
- [ ] Настроить базовые компоненты (shadcn/ui или custom):
  - Button, Input, Textarea
  - Select, Dropdown
  - Modal, Dialog
  - Toast/Notification
  - Spinner, Skeleton
- [ ] Создать `src/components/ui/`

**5.5 Layout**
- [ ] Создать `src/components/layout/Header.tsx`:
  - Логотип, навигация, user menu
- [ ] Создать `src/components/layout/Sidebar.tsx`:
  - Список диалогов, кнопка "Новый чат"
- [ ] Создать `src/app/layout.tsx`:
  - Общий layout с Header и Sidebar

**5.6 Страницы авторизации**
- [ ] Создать `src/app/(auth)/login/page.tsx`:
  - Форма логина (email, password)
  - Валидация, обработка ошибок
  - Редирект после успеха
- [ ] Создать `src/app/(auth)/register/page.tsx`:
  - Форма регистрации
  - Валидация email, password
- [ ] Создать middleware для protected routes

**5.7 Компоненты чата**
- [ ] Создать `src/components/chat/ChatContainer.tsx`:
  - Контейнер с MessageList и ChatInput
- [ ] Создать `src/components/chat/MessageList.tsx`:
  - Список сообщений с автоскроллом
- [ ] Создать `src/components/chat/MessageItem.tsx`:
  - Отображение сообщения (user/assistant)
  - Рендеринг Markdown
  - Подсветка кода (highlight.js)
- [ ] Создать `src/components/chat/ChatInput.tsx`:
  - Textarea с автовысотой
  - Кнопка отправки
  - Отправка по Enter (Shift+Enter для новой строки)

**5.8 Компоненты sidebar**
- [ ] Создать `src/components/sidebar/ConversationList.tsx`:
  - Список диалогов с пагинацией
  - Выделение активного диалога
- [ ] Создать `src/components/sidebar/ConversationItem.tsx`:
  - Название, дата, кнопка удаления
  - Кнопка/меню экспорта (JSON/Markdown)
- [ ] Создать `src/components/sidebar/NewChatButton.tsx`

**5.9 Селектор провайдера**
- [ ] Создать `src/components/chat/ProviderSelector.tsx`:
  - Выбор провайдера
  - Выбор модели (зависит от провайдера)
  - Настройки параметров (temperature, max_tokens)

**5.10 Страница чата**
- [ ] Создать `src/app/chat/page.tsx`:
  - Интеграция всех компонентов
  - Загрузка диалогов при монтировании
  - Обработка отправки сообщения

**5.11 Страница настроек**
- [ ] Создать `src/app/settings/page.tsx`:
  - Выбор темы (dark/light/system)
  - Провайдер и модель по умолчанию
  - Параметры генерации по умолчанию

**5.12 Баг-фиксы (обнаружены при тестировании)**
- [ ] Исправить сохранение ошибки между страницами:
  - Очищать `authStore.error` при навигации между `/login` и `/register`
  - Файл: `frontend/src/stores/authStore.ts` или компоненты страниц
- [ ] Исправить мобильную адаптацию:
  - Sidebar должен скрываться на мобильных устройствах
  - Добавить hamburger-меню для открытия sidebar
  - Файлы: `frontend/src/app/page.tsx`, `frontend/src/components/layout/Sidebar.tsx`

**5.13 Дополнительные элементы UI**
- [ ] Добавить переключатель темы (dark/light/system):
  - Кнопка в Header
  - Использовать существующий `settingsStore.theme`
  - Применять класс `dark` к `<html>` элементу
- [ ] Добавить кнопку "Очистить чат":
  - В интерфейсе чата или меню диалога
  - Удаление всех сообщений без удаления диалога
- [ ] Добавить favicon:
  - Создать `frontend/public/favicon.ico`
  - Или использовать SVG favicon в `frontend/src/app/layout.tsx`

**5.14 Проверка**
- [ ] Регистрация и логин работают
- [ ] Список диалогов загружается
- [ ] Сообщение отправляется и ответ отображается
- [ ] Новый чат создаётся
- [ ] Markdown и код рендерятся корректно
- [ ] Ошибки не сохраняются между страницами
- [ ] Мобильный интерфейс корректен (sidebar скрыт)
- [ ] Переключение темы работает

---

### Этап 6: Streaming
SSE на backend, streaming в провайдере, SSE клиент на frontend, анимация печатания, остановка генерации.

**Результат:** Ответы появляются по мере генерации

#### Задачи:

**6.1 Streaming в провайдере**
- [ ] Добавить в `DeepSeekProvider`:
  - Метод `chat_completion_stream()` → AsyncGenerator
  - Парсинг SSE от DeepSeek API
  - Yield каждого чанка текста
- [ ] Обработка ошибок при streaming

**6.2 SSE endpoint на backend**
- [ ] Создать `POST /api/chat/completions/stream`:
  - StreamingResponse с media_type `text/event-stream`
  - Формат событий: `data: {"content": "...", "done": false}\n\n`
  - Финальное событие: `data: {"done": true, "usage": {...}}\n\n`
- [ ] Интегрировать middleware pipeline со streaming
- [ ] Сохранять полный ответ в БД после завершения

**6.3 Остановка генерации (backend)**
- [ ] Создать механизм cancellation:
  - Хранить активные генерации в Redis (user_id → request_id)
  - При отмене — устанавливать флаг в Redis
  - Проверять флаг в цикле streaming
- [ ] Создать `POST /api/chat/stop`:
  - Принимает conversation_id или request_id
  - Устанавливает флаг отмены
- [ ] Корректно завершать stream при отмене

**6.4 SSE клиент на frontend**
- [ ] Создать `src/lib/streaming.ts`:
  - Функция `streamChat(request, onChunk, onDone, onError)`
  - Использовать fetch + ReadableStream (или EventSource)
  - Парсинг SSE событий
- [ ] Обработка переподключения при разрыве

**6.5 Обновление chatStore**
- [ ] Добавить в `chatStore`:
  - `isStreaming: boolean`
  - `streamingMessageId: string | null`
  - `streamingContent: string`
  - `abortController: AbortController | null`
- [ ] Метод `sendMessageStream()`:
  - Создать placeholder сообщение
  - Обновлять контент по мере получения чанков
  - Финализировать сообщение при done

**6.6 UI для streaming**
- [ ] Обновить `MessageItem.tsx`:
  - Отображать streaming контент
  - Курсор/индикатор печатания
- [ ] Обновить `ChatInput.tsx`:
  - Блокировать во время streaming
  - Показывать кнопку "Стоп" вместо "Отправить"
- [ ] Создать `src/components/chat/StopButton.tsx`:
  - Кнопка остановки генерации
  - Вызов `/api/chat/stop`

**6.7 Анимация**
- [ ] Добавить плавное появление текста (CSS transition)
- [ ] Мигающий курсор во время генерации
- [ ] Smooth scroll при добавлении контента

**6.8 Проверка**
- [ ] Текст появляется посимвольно/почанково
- [ ] Кнопка "Стоп" останавливает генерацию
- [ ] После остановки сообщение сохраняется частично
- [ ] Ошибки при streaming обрабатываются корректно
- [ ] UI не блокируется во время streaming

---

### Этап 7: Дополнительные провайдеры
Реализация OpenAI и Anthropic провайдеров, fallback при недоступности, UI выбора провайдера.

**Результат:** Пользователь может выбрать любого провайдера

#### Задачи:

**7.1 OpenAI провайдер**
- [ ] Создать `app/providers/openai.py`:
  - Реализовать `OpenAIProvider(BaseLLMProvider)`
  - Chat Completions API
  - Streaming через SSE
  - Список моделей: gpt-4o, gpt-4-turbo, gpt-3.5-turbo
- [ ] Маппинг параметров (совместимость с DeepSeek)
- [ ] Обработка ошибок (rate limit, quota)

**7.2 Anthropic провайдер**
- [ ] Создать `app/providers/anthropic.py`:
  - Реализовать `AnthropicProvider(BaseLLMProvider)`
  - Messages API (отличается от OpenAI)
  - Streaming
  - Список моделей: claude-3-opus, claude-3-sonnet, claude-3-haiku
- [ ] Конвертация формата сообщений (system prompt отдельно)
- [ ] Обработка ошибок

**7.3 Обновление реестра**
- [ ] Добавить OpenAI и Anthropic в реестр провайдеров
- [ ] Обновить конфигурацию (API ключи в .env)
- [ ] Добавить проверку наличия API ключа для активации провайдера

**7.4 Проверка доступности**
- [ ] Создать метод `health_check()` в BaseLLMProvider
- [ ] Реализовать для каждого провайдера:
  - Быстрый запрос к API для проверки ключа
  - Кэширование статуса в Redis (TTL 1 мин)
- [ ] Обновить `GET /api/providers/{id}/status`

**7.5 Fallback механизм**
- [ ] Создать конфигурацию fallback:
  - Порядок провайдеров для fallback
  - Условия переключения (timeout, error, rate_limit)
- [ ] Реализовать в chat service:
  - При ошибке — попытка следующего провайдера
  - Логирование fallback событий
  - Уведомление пользователя о смене провайдера

**7.6 UI выбора провайдера**
- [ ] Обновить `ProviderSelector.tsx`:
  - Отображение статуса провайдера (online/offline)
  - Группировка моделей по провайдеру
  - Иконки провайдеров
- [ ] Показывать информацию о модели:
  - Context window
  - Цена за токены (если есть)

**7.7 Сохранение предпочтений**
- [ ] Сохранять выбранный провайдер в conversation
- [ ] Сохранять дефолтный провайдер в user settings
- [ ] Применять user settings при создании нового чата

**7.8 Проверка**
- [ ] Переключение между провайдерами работает
- [ ] Streaming работает для всех провайдеров
- [ ] Fallback срабатывает при недоступности
- [ ] Статус провайдеров отображается корректно
- [ ] История сохраняет использованный провайдер

---

### Этап 8: Тестирование и оптимизация
Unit-тесты, интеграционные тесты, E2E тесты, нагрузочное тестирование, оптимизация, документация API.

**Результат:** Coverage > 80%, стабильная работа

#### Задачи:

**8.1 Настройка тестового окружения (Backend)**
- [ ] Настроить pytest с asyncio
- [ ] Создать `tests/conftest.py`:
  - Фикстуры для тестовой БД (SQLite in-memory или testcontainers)
  - Фикстуры для тестового клиента FastAPI
  - Фикстуры для мока провайдеров
- [ ] Настроить coverage отчёты

**8.2 Unit-тесты Backend**
- [ ] Тесты `services/auth.py`:
  - create_user, authenticate_user, password hashing
- [ ] Тесты `services/chat.py`:
  - send_message, контекст диалога
- [ ] Тесты `services/conversation.py`:
  - CRUD операции
- [ ] Тесты `providers/`:
  - Мок API ответов, парсинг, ошибки
- [ ] Тесты `middleware/`:
  - Pipeline, каждый middleware отдельно

**8.3 Интеграционные тесты Backend**
- [ ] Тесты auth endpoints:
  - register → login → me → refresh → logout
- [ ] Тесты chat endpoints:
  - Создание диалога → отправка сообщения → история
- [ ] Тесты providers endpoints
- [ ] Тесты middleware endpoints
- [ ] Тесты с реальной БД (PostgreSQL в Docker)

**8.4 Настройка тестового окружения (Frontend)**
- [ ] Настроить Vitest или Jest
- [ ] Настроить React Testing Library
- [ ] Создать моки для API
- [ ] Настроить coverage

**8.5 Unit-тесты Frontend**
- [ ] Тесты stores:
  - authStore, chatStore, settingsStore
- [ ] Тесты hooks:
  - useChat, useAuth
- [ ] Тесты компонентов:
  - MessageItem, ChatInput, ProviderSelector
- [ ] Тесты lib/api.ts:
  - Interceptors, error handling

**8.6 E2E тесты**
- [ ] Настроить Playwright
- [ ] Тест флоу регистрации/логина
- [ ] Тест отправки сообщения и получения ответа
- [ ] Тест streaming (ожидание появления текста)
- [ ] Тест смены провайдера
- [ ] Тест создания/удаления диалога

**8.7 Нагрузочное тестирование**
- [ ] Настроить Locust
- [ ] Сценарий: множество параллельных чатов
- [ ] Сценарий: streaming под нагрузкой
- [ ] Определить лимиты (RPS, concurrent users)
- [ ] Оптимизировать узкие места

**8.8 Оптимизация Backend**
- [ ] Кэширование в Redis:
  - Список провайдеров и моделей
  - Статус провайдеров
- [ ] Оптимизация запросов БД:
  - Индексы на часто используемые поля
  - N+1 проблемы
- [ ] Connection pooling (asyncpg, Redis)

**8.9 Оптимизация Frontend**
- [ ] Lazy loading страниц и компонентов
- [ ] Виртуализация списка сообщений (при большой истории)
- [ ] Оптимизация ре-рендеров (memo, useMemo)
- [ ] Сжатие бандла, tree-shaking

**8.10 Безопасность**
- [ ] Аудит зависимостей (npm audit, pip-audit)
- [ ] Проверка CORS настроек
- [ ] Проверка rate limiting
- [ ] Проверка валидации входных данных
- [ ] Проверка хранения секретов

**8.11 Документация**
- [ ] Настроить автогенерацию OpenAPI (Swagger UI)
- [ ] Описать все endpoints в docstrings
- [ ] Создать README с инструкцией:
  - Установка и запуск
  - Конфигурация
  - API документация
- [ ] Документация по добавлению нового провайдера

**8.12 Проверка**
- [ ] Coverage backend > 80%
- [ ] Coverage frontend > 70%
- [ ] Все E2E тесты проходят
- [ ] Нагрузочные тесты в пределах нормы
- [ ] Swagger UI доступен и актуален

---

## Зависимости этапов

```
[1] Инфраструктура
 │
 ▼
[2] Backend API
 │
 ▼
[3] DeepSeek
 │
 ├──────────┐
 ▼          ▼
[4]        [5]
Middleware  Frontend
 │          │
 └────┬─────┘
      ▼
[6] Streaming
      │
      ▼
[7] Провайдеры
      │
      ▼
[8] Тестирование
```

**Параллельно:** Этапы 4 и 5 можно выполнять одновременно

---

## Критерии готовности

| Версия | Этапы | Функционал |
|--------|-------|------------|
| MVP | 1-6 | Чат с DeepSeek, streaming, история, middleware |
| Full | 1-8 | + Несколько провайдеров, тесты, оптимизация |