# db-migrate

Управление миграциями базы данных через Alembic.

## Описание

Этот skill управляет миграциями:
- Создание новых миграций
- Применение миграций
- Откат миграций
- Просмотр истории

## Инструкции

При вызове `/db-migrate` определи действие из аргументов.

### Применить все миграции (по умолчанию)

```bash
cd backend
source venv/bin/activate 2>/dev/null || true
alembic upgrade head
```

### Создать новую миграцию

Аргумент: `new "описание"` или `create "описание"`

```bash
cd backend
source venv/bin/activate 2>/dev/null || true
alembic revision --autogenerate -m "описание миграции"
```

### Показать текущую версию

Аргумент: `current`

```bash
cd backend
source venv/bin/activate 2>/dev/null || true
alembic current
```

### История миграций

Аргумент: `history`

```bash
cd backend
source venv/bin/activate 2>/dev/null || true
alembic history --verbose
```

### Откатить последнюю миграцию

Аргумент: `downgrade` или `rollback`

```bash
cd backend
source venv/bin/activate 2>/dev/null || true
alembic downgrade -1
```

### Откатить до конкретной версии

Аргумент: `downgrade <revision>`

```bash
cd backend
source venv/bin/activate 2>/dev/null || true
alembic downgrade <revision_id>
```

### Откатить все

Аргумент: `reset`

⚠️ Предупреди пользователя об опасности!

```bash
cd backend
source venv/bin/activate 2>/dev/null || true
alembic downgrade base
```

### Показать SQL без выполнения

Аргумент: `sql`

```bash
cd backend
source venv/bin/activate 2>/dev/null || true
alembic upgrade head --sql
```

### Проверить состояние

Аргумент: `check`

```bash
cd backend
source venv/bin/activate 2>/dev/null || true
alembic check
```

## Важно

- Перед созданием миграции убедись, что модели SQLAlchemy обновлены
- После создания миграции **всегда** проверь сгенерированный файл
- Не применяй миграции на production без ревью

## Вывод

Сообщи пользователю:
- Текущую версию БД
- Какие миграции были применены/откачены
- Предупреждения об изменениях схемы