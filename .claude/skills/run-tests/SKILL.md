# run-tests

Запуск тестов для backend и frontend.

## Описание

Этот skill запускает тесты проекта:
- Backend: pytest
- Frontend: Jest/Vitest
- Покрытие кода
- Линтинг

## Инструкции

При вызове `/run-tests` определи scope из аргументов.

### Все тесты (по умолчанию)

```bash
# Backend тесты
cd backend
source venv/bin/activate 2>/dev/null || true
pytest -v

# Frontend тесты
cd frontend
npm test
```

### Только backend

Аргумент: `backend`

```bash
cd backend
source venv/bin/activate 2>/dev/null || true
pytest -v --tb=short
```

### Только frontend

Аргумент: `frontend`

```bash
cd frontend
npm test
```

### С покрытием

Аргумент: `coverage`

```bash
# Backend
cd backend
source venv/bin/activate 2>/dev/null || true
pytest --cov=app --cov-report=term-missing --cov-report=html

# Frontend
cd frontend
npm test -- --coverage
```

### Конкретный файл или тест

Аргумент: путь к файлу или паттерн

```bash
# Backend
pytest backend/tests/test_auth.py -v
pytest -k "test_login" -v

# Frontend
npm test -- --testPathPattern="auth"
```

### Линтинг

Аргумент: `lint`

```bash
# Backend
cd backend
source venv/bin/activate 2>/dev/null || true
ruff check .
mypy app/

# Frontend
cd frontend
npm run lint
npx tsc --noEmit
```

### Watch режим

Аргумент: `watch`

```bash
# Backend
pytest-watch

# Frontend
npm test -- --watch
```

## Вывод

Сообщи пользователю:
- Количество пройденных/проваленных тестов
- Процент покрытия (если запрошено)
- Детали упавших тестов
- Рекомендации по исправлению