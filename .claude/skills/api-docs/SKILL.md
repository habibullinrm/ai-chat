# api-docs

Генерация и просмотр документации API.

## Описание

Этот skill работает с документацией API:
- Открывает Swagger UI
- Экспортирует OpenAPI схему
- Генерирует клиентский код

## Инструкции

При вызове `/api-docs` определи действие из аргументов.

### Показать URL документации (по умолчанию)

Сообщи пользователю URL-ы документации:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Экспорт OpenAPI схемы

Аргумент: `export`

```bash
curl -s http://localhost:8000/openapi.json > api-schema.json
echo "Схема сохранена в api-schema.json"
```

### Экспорт в YAML

Аргумент: `yaml`

```bash
curl -s http://localhost:8000/openapi.json | python3 -c "
import sys, json, yaml
data = json.load(sys.stdin)
print(yaml.dump(data, allow_unicode=True, default_flow_style=False))
" > api-schema.yaml
```

### Генерация TypeScript клиента

Аргумент: `generate-client` или `client`

```bash
# Требует openapi-generator или openapi-typescript
npx openapi-typescript http://localhost:8000/openapi.json -o frontend/src/types/api.d.ts
```

### Валидация схемы

Аргумент: `validate`

```bash
# Проверка что сервер запущен и схема валидна
curl -s http://localhost:8000/openapi.json | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"API Version: {data.get('info', {}).get('version', 'unknown')}\")
    print(f\"Title: {data.get('info', {}).get('title', 'unknown')}\")
    paths = data.get('paths', {})
    print(f\"Endpoints: {len(paths)}\")
    for path in sorted(paths.keys()):
        methods = list(paths[path].keys())
        print(f\"  {path}: {', '.join(methods).upper()}\")
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"
```

### Список эндпоинтов

Аргумент: `list` или `endpoints`

```bash
curl -s http://localhost:8000/openapi.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
for path, methods in sorted(data.get('paths', {}).items()):
    for method, details in methods.items():
        summary = details.get('summary', 'No description')
        print(f'{method.upper():7} {path:40} {summary}')
"
```

## Требования

- Backend должен быть запущен на localhost:8000
- Для генерации клиента нужен openapi-typescript

## Вывод

Сообщи пользователю:
- URL документации
- Статус API (если запрошен экспорт)
- Путь к сгенерированным файлам