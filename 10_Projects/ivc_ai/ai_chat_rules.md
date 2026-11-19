---
type: project
project: ivc_ai
topic: sync
tags: [ivc_ai, project, sync, git]
created: 2026-11-19
updated: 2026-11-19
---

# ai_chat_rules: контекст для нового чата

Вставь блок ниже в начало новой сессии. Детали механики - [[sync_ops]].

```text
Проект ivc_ai. Windows ws024.zkh.local, vault C:\ivc_ai.
Репо: git@github.com:bjdanko5/ivc_ai.git (private, SSH), ветка main.
Автосинхронизация УЖЕ работает: Task Scheduler, задача ivc_ai_vault_backup, каждые 10 мин, tools\autocommit.cmd -> autocommit.cmd -> (see raw text below); commit+push без участия человека.
Ручная синхронизация: py -3 tools\ivc_git_sync.py -m "сообщение" --push; проверки: py -3 tools\ivc_check.py.
Pre-commit hook отключён (pre-commit.disabled), сканер секретов - заглушка без отчётов; push protection GitHub остаётся.
Утилиты: mknote.py (заметки), mkcard.py (карточки+код), run_wiki_lan.py (сайт LAN http://192.168.11.218:4000).
Источник правды по серверу: 20_Knowledge/Server_Setup/docs (01-10); команды - 07; ручной режим - 10.
Корень 20_Knowledge: hardware_procurement + knowledge.base. Эксплуатация: 10_Projects/ivc_ai (project_state, vault_map, site_ops, sync_ops, chat_playbook, ai_chat_rules).
Frontmatter: type/project/topic/tags/created/updated; models-теги на 05 и 08; Bases-фильтры только UI.
Сервер: Debian 13 headless, 9900X, RTX 5070 Ti 16GB, 64GB DDR5; NanoPlus 12.55GB + mmproj + mtp + chat_template.jinja; llama.cpp sm_120; Pi Agent ставит владелец.
Правила: только бесплатное; файлы через .py в C:\Temp или mknote/mkcard; без PowerShell-многострочников; код в VS Code; заметки со Связями; о безопасности секретов не напоминать.
Организация: АО ИВЦ ЖКХ; реальные данные клиентов/ПДн/ГИС ЖКХ в ИИ запрещены, только синтетика.
Инструкция для человека: chat_playbook (хочу X - скажи чату Y); механика синхронизации: sync_ops.
```

## Связи
- [[sync_ops]]
- [[chat_playbook]]
- [[vault_map]]
- [[project_state]]
- [[07_Automation_Scripts]]

