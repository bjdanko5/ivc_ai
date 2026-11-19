---
created: 2026-11-18
updated: 2026-11-19
tags:
  - knowledge
  - procurement
---

# Карта vault: что куда класть

| Папка | Назначение | Чем наполнять |
|---|---|---|
| 20_Knowledge/Server_Setup/docs | источник правды по серверу (01-10) | правки по факту; 07 = команды |
| 20_Knowledge корень | закупка + knowledge.base | статус закупки |
| 10_Projects/ivc_ai | статус, решения, карта | project_state, vault_map |
| 00_Inbox | сырые идеи и неразобранные выжимки | мысль сразу сюда |
| 30_Chats | архив чатов | Obsidian Web Clipper |
| 40_Cards | карточки скриптов | mkcard.py |
| code/scripts, code/py | код проекта | VS Code |
| 90_Templates | шаблоны | mknote.py |
| tools | утилиты vault | без нужды не трогать |
| logs | отчёты (git-ignored) |自动生成 |

## Правила
- Новые факты про сервер - только в docs/. Корневые заметки 20_Knowledge не плодить.
- Инфраструктурные заметки заканчиваются блоком Связи.
- Bases: в YAML только name/description/columns/sort; фильтры и колонки - через UI.

## Почему knowledge.base не видел docs
Фильтр папки в UI стоял на 20_Knowledge (точно), а заметки уехали в 20_Knowledge/Server_Setup/docs. Лечение в UI: фильтр file.folder contains 20_Knowledge (или снять фильтр папки), колонку file.folder добавить там же. YAML базы не менять.

## Связи
- [[project_state]]
- [[07_Automation_Scripts]]
- [[hardware_procurement]]

