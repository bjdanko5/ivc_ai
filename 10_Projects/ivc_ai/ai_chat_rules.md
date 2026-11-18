---
type: knowledge
project: ivc_ai
topic: ai-chat-rules
created: 2026-11-18
tags: [knowledge, rules, workflow]
---

# Правила работы с ИИ по проекту ivc_ai

Вставляй этот блок в начало каждого нового чата с ИИ по проекту.

## Преамбула для ИИ

    Проект ivc_ai: правила работы

    1. Хранилище: Obsidian vault + Git на C:\ivc_ai.
    2. Безопасность: Пароли и токены — только в KeePassXC или локальном .env (git-ignored). В заметках и коде — только ссылки на записи KeePassXC. Секреты никогда не коммитить.
    3. Создание файлов: Все новые файлы (заметки, скрипты, конфиги) создавай через отдельные .py-файлы в C:\temp\, которые пишут контент через Path.write_text(encoding="utf-8"). Никогда не используй PowerShell -c с многострочным текстом, here-string’и или большие PS1-скрипты с кириллицей — они ломают кодировку и синтаксис при вставке.
    4. Команды:
       - Проверка: py -3 C:\ivc_ai\tools\ivc_check.py
       - Коммит: py -3 C:\ivc_ai\tools\ivc_git_sync.py -m "сообщение"
       - Коммит+пуш: py -3 C:\ivc_ai\tools\ivc_git_sync.py -m "сообщение" --push
    5. Инструменты: Только бесплатные. Платные решения не предлагать.
    6. Язык заметок: В Obsidian пишу по-русски. Шаблоны и служебные скрипты — ASCII-only для совместимости.
    7. Создание заметок: py -3 C:\ivc_ai\tools\mknote.py <путь> [заголовок]
    8. Создание карточек скриптов: py -3 C:\ivc_ai\tools\mkcard.py <имя> <lang> [описание]
    9. Bases (.base файлы): НЕ использовать filters в YAML (нестабильный синтаксис).
    Только columns + sort. Фильтрация — через UI Bases 
    При создании .base: только name, description, columns, sort. Без filters, без width.
    10. Фильтры: and/or + property + operator (is/includes/contains) + value.
    11. НЕ использовать width, order. Использовать direction для сортировки.
    12. При создании/изменении .base всегда проверяй актуальный синтаксис.
    13. Скрипты в code/ НЕ открывать в Obsidian (Detect all file extensions = OFF).
    Редактировать только в VS Code. В Obsidian видны только карточки из 40_Cards/. 

## Почему именно такой подход

- PowerShell here-string и кириллица в .ps1 ломаются при копировании из чата (кодировка ANSI vs UTF-8, терминаторы here-string съезжают).
- Python Path.write_text(encoding="utf-8") надёжен независимо от кодировки терминала.
- Отдельный .py файл в C:\temp\ легко создать, проверить и удалить после использования.
- ASCII-only в служебных файлах исключает проблемы кодировки навсегда.

## Связанные заметки

- [[daily_commands]]
