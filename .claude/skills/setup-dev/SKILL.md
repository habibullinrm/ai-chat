# setup-dev

Инициализация окружения разработки для проекта AI-Chat.

## Описание

Этот skill настраивает полное окружение разработки:
- Создаёт виртуальное окружение Python
- Устанавливает backend зависимости
- Устанавливает frontend зависимости
- Проверяет наличие необходимых инструментов

## Инструкции

При вызове `/setup-dev` выполни следующие шаги:

### 1. Проверка инструментов

Проверь наличие:
- Python 3.11+
- Node.js 18+
- npm или pnpm
- Docker и Docker Compose

```bash
python3 --version
node --version
npm --version
docker --version
docker-compose --version
```

### 2. Backend настройка

```bash
cd backend

# Создание виртуального окружения
python3 -m venv venv

# Активация и установка зависимостей
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # если есть
```

### 3. Frontend настройка

```bash
cd frontend

# Установка зависимостей
npm install

# Или с pnpm
# pnpm install
```

### 4. Переменные окружения

Скопируй `.env.example` в `.env` если он существует:

```bash
cp .env.example .env 2>/dev/null || echo "Создай .env файл вручную"
```

### 5. База данных

Если Docker доступен:
```bash
docker-compose up -d db redis
```

### 6. Миграции

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

## Вывод

После выполнения сообщи пользователю:
- Статус установки каждого компонента
- Какие переменные окружения нужно настроить
- Следующие шаги для запуска проекта