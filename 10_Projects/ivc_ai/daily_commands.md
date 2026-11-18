---
type: knowledge
project: ivc_ai
topic: daily-commands
created: 2026-11-18
tags: [knowledge, commands]
---

# Ежедневные команды ivc_ai

## Проверка vault

Проверяет структуру, Git, синтаксис Python, секреты.

    py -3 C:\ivc_ai\tools\ivc_check.py

## Коммит с проверками

Полная проверка -> git add -> staged-проверка -> commit.

    py -3 C:\ivc_ai\tools\ivc_git_sync.py -m "описание изменений"

## Коммит + пуш в GitHub

То же + push. Требует настроенный remote.

    py -3 C:\ivc_ai\tools\ivc_git_sync.py -m "описание изменений" --push

## Подключение GitHub (одноразово)

1. Создай пустой private репозиторий ivc_ai на GitHub (без README/.gitignore).
2. Выполни:

        cd C:\ivc_ai
        git remote add origin https://github.com/YOUR_USERNAME/ivc_ai.git
        git push -u origin main

Токен GitHub храни в KeePassXC, не в заметках.

## Сканирование секретов отдельно

Весь vault:

    py -3 C:\ivc_ai\tools\ivc_secret_scan.py --root C:\ivc_ai

Только staged-файлы:

    py -3 C:\ivc_ai\tools\ivc_secret_scan.py --root C:\ivc_ai --staged

Отчёты сохраняются в logs/scan_*.json.

## Правило безопасности

Пароли и токены НЕ хранить в vault.
Секреты: KeePassXC (основное) + локальный .env (исключён из Git).
В заметках только ссылка: HF token -> KeePassXC entry hf-token.
