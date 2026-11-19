---
type: knowledge
project: ivc_ai
topic: client-workstation
hostname: ws024
ip: 192.168.11.218
created: 2026-11-18
tags: [knowledge, client, workstation]
---

# Клиентская рабочая станция ws024

> Это НЕ сервер для ИИ. Это точка входа для разработки.

## Характеристики

| Параметр | Значение |
|----------|---------|
| Имя | ws024.zkh.local |
| IP | 192.168.11.218 |
| CPU | Intel Pentium G4560 @ 3.50 GHz (2C/4T) |
| RAM | 16 GB DDR4 |
| SSD | WD Green 2.5 1000 GB |
| HDD | Seagate ST3250318AS 233 GB |
| GPU | Intel HD Graphics 610 (128 MB shared) |
| ОС | Windows x64 |

## Роль в архитектуре ivc_ai

- VS Code + Remote SSH -> подключение к Debian-серверу
- Pi Agent работает НА СЕРВЕРЕ, не здесь
- Локально: только редактор, git-клиент, браузер
- Никаких моделей на этой машине не запускать

## Подключение к серверу ИИ

SSH config (~/.ssh/config):

    Host ivc-server
        HostName <IP-адрес-нового-сервера>
        User <username>
        IdentityFile ~/.ssh/id_ed25519
        Port 22
        ServerAliveInterval 60
        LocalForward 8080 localhost:8080

> IP нового сервера (Ryzen 9900X + RTX 5070 Ti) внести после ввода в эксплуатацию.

## Ограничения

- GPU отсутствует (Intel HD 610 не поддерживает CUDA/inference)
- 16 GB RAM достаточно только для IDE + браузера
- Не хранить модели, не запускать llama.cpp локально
- Все вычисления ИИ — только на удалённом Debian-сервере

## Связанные

- [[09_Client_File_Delivery]]
- [[03_System_Configuration]]
