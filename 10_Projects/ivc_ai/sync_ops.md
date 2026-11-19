---
type: project
project: ivc_ai
topic: sync
tags: [ivc_ai, project, sync, git]
created: 2026-11-19
updated: 2026-11-19
---

# Эксплуатация: Git-синхронизация vault

## Что работает сейчас (обнаружено автоматически)
- Remote:
```text
origin	git@github.com:bjdanko5/ivc_ai.git (fetch)
origin	git@github.com:bjdanko5/ivc_ai.git (push)
```
- Ветка: main
- Последние коммиты:
```text
b9f2b63 vault backup: 19.11.2026 16:25:27,42
3f3de13 housekeeping: topic tags, site_ops+playbook+ai_chat_rules, launcher in tools, scan reports off
892135e vault backup: 19.11.2026 16:15:27,60
```
- Задача: ivc_ai_vault_backup | State: Ready
  - Действие: C:\ivc_ai\tools\autocommit.cmd 
  - Интервал повтора: PT10M
- Цепочка: autocommit.cmd -> (see raw text below) (проверки ivc_check.py, затем commit и push -u origin main).
- Pre-commit hook: отключён (pre-commit.disabled сохранён)
- Сканер секретов: заглушка, отчёты не пишутся
- .gitignore:
```text
.env
.env.*
!.env.example
*.kdbx
*.key
*.pem
*.p12
*.pfx
secrets/
private/
credentials/
token.txt
tokens.txt
.venv/
venv/
__pycache__/
*.pyc
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.trash/
logs/
*.log
*.tmp
Thumbs.db
```

## Содержимое autocommit.cmd
```bat
@echo off

chcp 65001 >nul

cd /d C:\ivc_ai

git add -A

for /f %%i in ('git diff --cached --name-only') do set CHANGED=1

if defined CHANGED (

    git commit -m "vault backup: %date% %time%"

    git push origin main 2>nul

) else (

    echo [OK] nothing to commit

)
```

## Опции ivc_git_sync.py (из исходника)
```text
add_argument("-m", "--message", default="ivc_ai update")
add_argument("--push", action="store_true")
```

## Ручные команды
```bat
git -C C:\ivc_ai status -sb
git -C C:\ivc_ai log --oneline -5
py -3 C:\ivc_ai\tools\ivc_check.py
py -3 C:\ivc_ai\tools\ivc_git_sync.py -m "сообщение" --push
```

## Пауза и возобновление автокоммита
```bat
schtasks /change /tn "ivc_ai_vault_backup" /disable
schtasks /change /tn "ivc_ai_vault_backup" /enable
schtasks /query /tn "ivc_ai_vault_backup" /fo LIST /v
```
Если имя задачи отличается - подставить фактическое из раздела выше.

## Если автокоммит молчит
1. State задачи (Ready/Disabled) и LastTaskResult: Get-ScheduledTaskInfo -TaskName "ivc_ai_vault_backup"
2. Прогнать ivc_git_sync.py вручную - он печатает причину остановки.
3. Сверить время последнего коммита с ожидаемым интервалом (10 мин).

## Если push отклонён (GH013)
Локальный сканер отключён, поэтому блокирует только GitHub push protection. В выводе push есть ссылка unblock-secret - открыть, разрешить, повторить push. Либо вынести секрет из коммита (git reset --soft HEAD~1 и новый коммит).

## Инвентарь скриптов
| Скрипт | Роль |
|---|---|
| tools/autocommit.cmd | точка входа Task Scheduler (silent) |
| tools/ivc_git_sync.py | проверки + commit + push |
| tools/ivc_check.py | структура vault, .gitignore, наличие утилит, скан |
| tools/ivc_secret_scan.py | заглушка (оригинал .disabled) |
| tools/mknote.py | заметка с frontmatter |
| tools/mkcard.py | карточка скрипта + файл кода |
| tools/run_wiki_lan.py | сайт-руководство в LAN |

## Связи
- [[vault_map]]
- [[site_ops]]
- [[chat_playbook]]
- [[ai_chat_rules]]
- [[project_state]]

