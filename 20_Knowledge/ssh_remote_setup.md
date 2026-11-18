---
type: knowledge
project: ivc_ai
topic: ssh-remote
created: 2026-11-18
tags: [knowledge, ssh, vscode, remote]
---

# SSH Remote: Windows -> Debian

## Архитектура

    [Windows PC]                    [Debian Server]
    VS Code + Pi Agent  ---SSH--->  llama-server + GPU
    Редактирование кода             Инференс модели
    Git операции                    Модели в /opt/ivc_ai/models/

## Настройка SSH (Windows side)

### 1. Генерация ключа (если нет)

    ssh-keygen -t ed25519 -C "ivc_ai"

### 2. Копирование ключа на сервер

    ssh-copy-id user@server-ip

### 3. SSH config (~/.ssh/config)

    Host ivc-server
        HostName <server-ip>
        User <username>
        IdentityFile ~/.ssh/id_ed25519
        Port 22
        ServerAliveInterval 60
        ServerAliveCountMax 3
        ForwardAgent yes

### 4. Подключение в VS Code

1. Установить расширение Remote - SSH
2. Ctrl+Shift+P -> Remote-SSH: Connect to Host -> ivc-server
3. Открыть папку ~/projects/ или /opt/ivc_ai/

## Настройка сервера (Debian side)

### SSH hardening (/etc/ssh/sshd_config)

    PasswordAuthentication no
    PubkeyAuthentication yes
    PermitRootLogin no
    MaxAuthTries 3
    ClientAliveInterval 60
    ClientAliveCountMax 3

Перезапуск: sudo systemctl restart sshd

### Firewall (ufw)

    sudo ufw allow 22/tcp
    sudo ufw enable

## Проброс порта llama-server (опционально)

Если нужен доступ к API с Windows (для AnythingLLM/Khoj):

В SSH config добавить:

    LocalForward 8080 localhost:8080

Или при подключении:

    ssh -L 8080:localhost:8080 ivc-server

Тогда на Windows: http://localhost:8080/v1/chat/completions

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| Connection refused | Проверить sshd status, ufw, IP |
| Permission denied | Проверить ~/.ssh/authorized_keys, права 700/600 |
| Disconnects | ServerAliveInterval в config, проверить сеть |
| Slow transfer | Проверить MTU, использовать Compression yes |
| GPU not visible over SSH | Убедиться что nvidia-smi работает в SSH-сессии |

## Связанные

- [[server_debian_profile]]
- [[pi_agent_config]]
