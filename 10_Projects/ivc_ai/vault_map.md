---
type: project
project: ivc_ai
created: 2026-11-19
updated: 2026-11-19
---

# Карта vault: что куда класть

| Папка/файл | Назначение | Чем наполнять |
|---|---|---|
| 20_Knowledge/Server_Setup/docs | источник правды по серверу (01-10) | правки по факту; 07 = команды |
| 20_Knowledge корень | hardware_procurement + knowledge.base | статус закупки |
| 10_Projects/ivc_ai | project_state, vault_map, site_ops, chat_playbook, ai_chat_rules | статус и эксплуатация |
| 00_Inbox | сырые идеи | мысль сразу сюда |
| 30_Chats | архив чатов | Web Clipper |
| 40_Cards + code | карточки и код | mkcard.py; VS Code |
| 90_Templates | шаблоны | mknote.py |
| tools | утилиты vault, включая run_wiki_lan.py | без нужды не трогать |
| logs | пусто (генерация отчётов отключена) | - |

## Frontmatter и Bases
- Схема: type / project / topic / tags / created / updated.
- Примеры UI-фильтров: tags contains models; topic is hardware; file.folder contains Server_Setup/docs.
- YAML базы: только name/description/columns/sort; фильтры и колонки - UI.

## Связи
- [[project_state]]
- [[site_ops]]
- [[chat_playbook]]
- [[ai_chat_rules]]
- [[07_Automation_Scripts]]

