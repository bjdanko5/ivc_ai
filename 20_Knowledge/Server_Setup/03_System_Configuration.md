---
created: 2026-11-19
tags:
  - linux
  - config
  - ssh
---

# Часть 3: Базовая настройка системы

## 3.1. Пользователь и каталоги
```bash
mkdir -p ~/src ~/downloads ~/models ~/projects
```

## 3.2. Сеть и SSH
- Настроить статический IP или убедиться в работе DHCP.
- Включить вход по ключам SSH (`PasswordAuthentication no`).

## 3.3. Обновление и драйверы сети
- Если сеть не работает из коробки, использовать backports или USB-модем для загрузки firmware-realtek.

## Связи
- [[Debian_Server_Setup]]
- [[02_Debian_Installation]]
- [[04_NVIDIA_Drivers]]
