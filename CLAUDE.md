# AI-Chat

Веб-приложение для асинхронного общения с LLM (DeepSeek, OpenAI, Anthropic) с поддержкой middleware pipeline.

## Технологии

| Компонент | Стек |
|-----------|------|
| Frontend | Next.js 14+, TypeScript, Tailwind CSS, Zustand, Zod |
| Backend | Python 3.11+, FastAPI, SQLAlchemy (async), Pydantic |
| БД | PostgreSQL, Redis |
| Инфраструктура | Docker, Docker Compose |

## Структура проекта

```
ai-chat/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI приложение
│   │   ├── config.py        # Настройки (pydantic-settings)
│   │   ├── api/v1/          # Эндпоинты
│   │   ├── models/          # SQLAlchemy модели
│   │   ├── schemas/         # Pydantic схемы
│   │   ├── services/        # Бизнес-логика
│   │   ├── providers/       # LLM провайдеры (DeepSeek, OpenAI, Anthropic)
│   │   └── middleware/      # Middleware pipeline
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/             # Next.js App Router
│       ├── components/      # React компоненты
│       ├── stores/          # Zustand stores
│       ├── hooks/           # Custom hooks
│       ├── lib/             # API клиент, утилиты
│       └── types/           # TypeScript типы
├── docker-compose.yml
└── .env
```

## Команды

```bash
# Запуск всего проекта
docker compose up -d

# Backend отдельно
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend отдельно
cd frontend && npm run dev

# Миграции
cd backend && alembic upgrade head

# Тесты
cd backend && pytest
cd frontend && npm test
```

## Переменные окружения

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/aichat
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM Providers
DEEPSEEK_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-xxx
```

## Архитектура

```
Frontend (Next.js) → Backend (FastAPI) → LLM Providers
                           ↓
                    Middleware Pipeline
```

- **Middleware Pipeline** — цепочка обработчиков pre/post для сообщений
- **Providers** — абстракция над LLM API с единым интерфейсом
- **Streaming** — SSE для потоковой передачи ответов

## Ключевые файлы

### Backend
- `app/providers/base.py` — абстрактный класс провайдера
- `app/middleware/pipeline.py` — конвейер обработки
- `app/api/v1/chat.py` — эндпоинты чата
- `app/core/security.py` — JWT авторизация

### Frontend
- `src/stores/chatStore.ts` — состояние чата
- `src/hooks/useChat.ts` — логика чата и streaming
- `src/components/chat/` — компоненты чата

## API

Основные эндпоинты:

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/auth/login` | Авторизация |
| POST | `/api/chat/completions` | Отправка сообщения |
| POST | `/api/chat/completions/stream` | Streaming ответ |
| GET | `/api/conversations` | Список диалогов |
| GET | `/api/providers` | Список провайдеров |

Полная документация: `GET /docs` (Swagger UI)

## Conventions

- Backend: snake_case, типизация через Pydantic
- Frontend: camelCase, TypeScript strict mode
- API версионирование: `/api/v1/`
- Коммиты: conventional commits (feat, fix, docs, refactor)
- Документация и комментарии: русский язык