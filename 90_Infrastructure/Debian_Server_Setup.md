---
created: 2026-11-18
tags:
  - infrastructure
  - debian
  - server
  - nvidia
---

# Настройка сервера ИИ: Debian 12

## Инфраструктура
- **Железо:** Ryzen 9 9900X, RTX 5070 Ti 16GB, 64GB DDR5
- **ОС:** Debian 12 "Bookworm" (Stable)
- **Интерфейс:** Headless (без GUI), управление через SSH

## Почему Debian 12?
- Максимальная стабильность для серверной среды.
- Поддержка нового железа (Ryzen 9000) в ядре.
- Лучшая совместимость с проприетарными драйверами NVIDIA для новых карт (RTX 50-series).

## Оптимальная разметка диска
Рекомендуется **Ext4** для простоты и надёжности.

- `/boot/efi` — 512 MB (FAT32, загрузчик)
- `/` — 50-100 GB (Ext4, система и ПО)
- `swap` — 64 GB (равно объёму RAM, резерв при нехватке VRAM)
- `/opt/ivc_ai` — всё остальное место (модели и данные проекта)

## Установка и базовая настройка
1. **ISO:** Использовать Debian 12 Netinst.
2. **Пакеты:** При установке выбрать только "SSH server" и "standard system utilities".
3. **Драйверы NVIDIA:**
   - Добавить `non-free-firmware` в источники APT.
   - Установить последние драйверы с сайта NVIDIA или из Backports.
   - Установить `nvidia-cuda-toolkit`.

## Оптимизация производительности

### AMD Ryzen 9 9900X
- В BIOS включить режим производительности (Performance Mode).
- Включить Transparent Huge Pages:
```bash
echo 'vm.nr_hugepages = 1024' >> /etc/sysctl.conf
sysctl -p
```

### Структура папок на сервере
```bash
mkdir -p /opt/ivc_ai/models
mkdir -p /opt/ivc_ai/logs
chown -R $USER:$USER /opt/ivc_ai
```

## Сеть и безопасность
- Настроить статический IP.
- Включить аутентификацию по ключам SSH (PasswordAuthentication no).
- Подключение с ws024 через VS Code Remote SSH.

## Текущий статус
- [ ] Скачан ISO образ
- [ ] Создана загрузочная флешка
- [ ] Выполнена базовая установка ОС
- [ ] Установлены драйверы NVIDIA
- [ ] Настроен доступ по SSH

## Связи
- [[Project Map]]
- [[Hardware Specs]]
- [[Local AI Setup]]
