# docker-build

Сборка и управление Docker контейнерами проекта AI-Chat.

## Описание

Этот skill управляет Docker окружением:
- Сборка образов
- Запуск контейнеров
- Просмотр логов
- Остановка и очистка

## Инструкции

При вызове `/docker-build` определи нужное действие из аргументов.

### Действия

#### Полная сборка и запуск (по умолчанию)

```bash
docker-compose build
docker-compose up -d
```

#### Только сборка

Аргумент: `build`

```bash
docker-compose build --no-cache
```

#### Запуск

Аргумент: `up`

```bash
docker-compose up -d
```

#### Остановка

Аргумент: `down`

```bash
docker-compose down
```

#### Просмотр логов

Аргумент: `logs` или `logs <service>`

```bash
# Все сервисы
docker-compose logs -f --tail=100

# Конкретный сервис
docker-compose logs -f --tail=100 backend
```

#### Перезапуск

Аргумент: `restart`

```bash
docker-compose restart
```

#### Статус

Аргумент: `status`

```bash
docker-compose ps
docker-compose top
```

#### Очистка

Аргумент: `clean`

```bash
docker-compose down -v --rmi local
docker system prune -f
```

### Отдельные сервисы

Можно указать сервис: `backend`, `frontend`, `db`, `redis`

```bash
docker-compose build backend
docker-compose up -d backend
```

## Проверка здоровья

После запуска проверь:

```bash
# Backend API
curl -s http://localhost:8000/health || echo "Backend не отвечает"

# Frontend
curl -s http://localhost:3000 || echo "Frontend не отвечает"

# PostgreSQL
docker-compose exec db pg_isready || echo "DB не готова"

# Redis
docker-compose exec redis redis-cli ping || echo "Redis не отвечает"
```

## Вывод

Сообщи пользователю:
- Статус каждого контейнера
- URL для доступа к сервисам
- Ошибки если есть