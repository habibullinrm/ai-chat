#!/bin/bash
# Hook: Автоформатирование файлов после редактирования
# Использование: auto-format.sh "$CLAUDE_FILE_PATHS"

FILE_PATHS="$1"

# Если пути пустые, выходим
if [ -z "$FILE_PATHS" ]; then
    exit 0
fi

# Функция для форматирования Python файлов
format_python() {
    local file="$1"

    # Пробуем ruff (быстрее)
    if command -v ruff &> /dev/null; then
        ruff format "$file" 2>/dev/null
        ruff check --fix "$file" 2>/dev/null
        return
    fi

    # Fallback на black
    if command -v black &> /dev/null; then
        black --quiet "$file" 2>/dev/null
    fi

    # isort для импортов
    if command -v isort &> /dev/null; then
        isort --quiet "$file" 2>/dev/null
    fi
}

# Функция для форматирования JS/TS файлов
format_javascript() {
    local file="$1"

    # Пробуем prettier
    if command -v prettier &> /dev/null; then
        prettier --write "$file" 2>/dev/null
        return
    fi

    # Или через npx
    if command -v npx &> /dev/null; then
        npx prettier --write "$file" 2>/dev/null
    fi
}

# Функция для форматирования JSON файлов
format_json() {
    local file="$1"

    if command -v prettier &> /dev/null; then
        prettier --write "$file" 2>/dev/null
    elif command -v jq &> /dev/null; then
        # jq для форматирования JSON
        tmp=$(mktemp)
        if jq '.' "$file" > "$tmp" 2>/dev/null; then
            mv "$tmp" "$file"
        else
            rm -f "$tmp"
        fi
    fi
}

# Обработка каждого файла
IFS=',' read -ra FILES <<< "$FILE_PATHS"
for file in "${FILES[@]}"; do
    # Убираем пробелы
    file=$(echo "$file" | xargs)

    # Проверяем существование файла
    if [ ! -f "$file" ]; then
        continue
    fi

    # Определяем тип файла по расширению
    extension="${file##*.}"

    case "$extension" in
        py)
            format_python "$file"
            ;;
        js|jsx|ts|tsx|mjs|cjs)
            format_javascript "$file"
            ;;
        json)
            format_json "$file"
            ;;
        css|scss|less)
            format_javascript "$file"  # prettier поддерживает CSS
            ;;
        md|mdx)
            format_javascript "$file"  # prettier поддерживает Markdown
            ;;
        yaml|yml)
            format_javascript "$file"  # prettier поддерживает YAML
            ;;
    esac
done

exit 0