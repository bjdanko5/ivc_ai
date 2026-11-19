---
created: 2026-11-19
tags:
  - debian
  - installation
  - lvm
---

# Часть 2: Установка Debian 13 (Trixie)

## 2.1. Подготовка
- **Образ:** `debian-13.7.0-amd64-netinst.iso` (firmware включена)
- **Загрузчик:** Ventoy
- **Сеть:** Возможна проблема с Realtek RTL8125D (XID 0x689). Иметь под рукой USB-модем.

## 2.2. Параметры установки
- **Root пароль:** ПУСТО (для активации sudo)
- **Пакеты:** Только `SSH server` и `standard system utilities` (без GUI)

## 2.3. Разметка диска (LVM)
| Устройство | Размер | ФС | Точка | Примечание |
|---|---|---|---|---|
| nvme0n1p1 | 1 GiB | FAT32 | /boot/efi | ESP |
| nvme0n1p2 | 2 GiB | ext4 | /boot | Отдельный раздел |
| vg0/lv_root | 60 GiB | ext4 | / | Система |
| vg0/lv_var | 30 GiB | ext4 | /var | Логи, reserved 1% |
| vg0/lv_docker | 150 GiB | ext4 | /var/lib/docker | Отдельный том для Docker |
| vg0/lv_home | 400 GiB | ext4 | /home | Проекты, модели, кэши |
| vg0/lv_swap | 8 GiB | swap | — | Резерв + zram |

**Важно:** `lv_docker` и `lv_home` в установщике помечать как "do not use". Форматировать вручную позже с нужными параметрами inode.

## Связи
- [[Debian_Server_Setup]]
- [[01_BIOS_Preparation]]
- [[03_System_Configuration]]
