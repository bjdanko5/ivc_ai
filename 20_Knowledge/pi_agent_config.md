---
type: knowledge
project: ivc_ai
topic: pi-agent
agent_version: 1.5.2
created: 2026-11-18
tags: [knowledge, pi-agent, coding-agent, local_ai]
---

# Pi Agent v1.5.2 — конфигурация для ivc_ai

## Обзор

Pi Agent — терминальный AI-агент для кодинга. Работает на Debian-сервере,
подключается к локальному llama-server с Cyber-Tiel-Coder-35B-A3B.

## Загруженные расширения

| Расширение | Назначение |
|------------|-----------|
| @d4rw1nz/pi-custom-provider | Подключение к кастомному llama-server |
| @timonclaeys/pi-github-skill-installer | Установка скиллов из GitHub |
| @yan-sheng-li/pi-codegraph-fix | Фикс codegraph |
| pi-llama-server | Нативная интеграция с llama-server |
| pi-message-timestamp | Временные метки сообщений |

## Контекстные файлы

Pi автоматически загружает при старте:

    ~/.pi/agent/AGENTS.md   # глобальные инструкции агента
    ./AGENTS.md             # проектные инструкции (в корне репо)

## Настройка custom provider (llama-server)

В ~/.pi/agent/config.json или через переменные окружения:

    {
      "provider": "custom",
      "customProvider": {
        "baseUrl": "http://localhost:8080",
        "model": "Cyber-Tiel-Coder-35B-A3B-Q5_K_M",
        "maxTokens": 4096,
        "temperature": 0.2
      }
    }

Для кодирования temperature 0.2-0.3 оптимальна.

## Запуск llama-server для Pi

На Debian-сервере:

    /opt/ivc_ai/llama.cpp/build/bin/llama-server \
      -m /opt/ivc_ai/models/Cyber-Tiel-Coder-35B-A3B-Q5_K_M.gguf \
      -ngl 99 \
      -c 8192 \
      -t 12 \
      --host 127.0.0.1 \
      --port 8080 \
      --chat-template chatml

Как systemd-сервис (/etc/systemd/system/llama-server.service):

    [Unit]
    Description=llama.cpp server for ivc_ai
    After=nvidia-persistenced.service

    [Service]
    Type=simple
    User=ivc
    ExecStart=/opt/ivc_ai/llama.cpp/build/bin/llama-server \
      -m /opt/ivc_ai/models/Cyber-Tiel-Coder-35B-A3B-Q5_K_M.gguf \
      -ngl 99 -c 8192 -t 12 \
      --host 127.0.0.1 --port 8080 \
      --chat-template chatml
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=multi-user.target

    sudo systemctl enable --now llama-server

## AGENTS.md — шаблон для проекта

Создать в корне каждого репозитория:

    # Project: <name>

    ## Rules
    - Language: Python 3.10+ / PowerShell / Bash
    - Style: type hints, docstrings
    - Tests: pytest for Python
    - No secrets in code -> KeePassXC references only
    - Commit messages: conventional commits

    ## Architecture
    <описание структуры проекта>

    ## Conventions
    <специфичные соглашения>

Pi читает этот файл при каждом запуске и учитывает правила.

## Горячие клавиши Pi

| Клавиша | Действие |
|---------|---------|
| Ctrl+C / Ctrl+D | Прервать / выйти |
| Ctrl+O | Полная справка |
| / | Команды Pi |
| ! | Bash-команда прямо в Pi |
| Escape | Interrupt |

## Workflow: типичная сессия

1. SSH в сервер: ssh ivc-server
2. Перейти в проект: cd ~/projects/my-project
3. Запустить Pi: pi
4. Pi читает AGENTS.md, подключается к llama-server
5. Работа: правка кода, генерация тестов, ревью
6. Коммит: ! git add -A && git commit -m "feat: ..."
7. Выход: Ctrl+D

## Связанные

- [[server_debian_profile]]
- [[ssh_remote_setup]]
- [[model_cyber_tiel_coder]]
- [[llamacpp_platform]]
