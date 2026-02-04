#!/bin/bash
# Hook: Блокировка опасных команд
# Использование: block-dangerous.sh "$CLAUDE_BASH_COMMAND"

COMMAND="$1"

# Список опасных паттернов
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf /*"
    "rm -rf ~"
    "rm -rf \$HOME"
    "rm -rf ."
    "rm -rf .."
    ":(){:|:&};:"          # Fork bomb
    "dd if=/dev/zero"
    "mkfs."
    "DROP TABLE"
    "DROP DATABASE"
    "TRUNCATE TABLE"
    "DELETE FROM .* WHERE 1"
    "chmod -R 777 /"
    "chown -R .* /"
    "> /dev/sda"
    "wget .* | sh"
    "curl .* | sh"
    "wget .* | bash"
    "curl .* | bash"
)

# Проверка команды на опасные паттерны
for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        echo "BLOCKED: Опасная команда обнаружена!"
        echo "Паттерн: $pattern"
        echo "Команда: $COMMAND"
        exit 2  # Код 2 блокирует выполнение
    fi
done

# Предупреждение для потенциально опасных команд
WARNING_PATTERNS=(
    "rm -rf"
    "DROP"
    "TRUNCATE"
    "--force"
    "--hard"
    "reset --hard"
    "push --force"
    "push -f"
)

for pattern in "${WARNING_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        echo "WARNING: Потенциально опасная команда"
        echo "Паттерн: $pattern"
        # Не блокируем, только предупреждаем
        break
    fi
done

exit 0