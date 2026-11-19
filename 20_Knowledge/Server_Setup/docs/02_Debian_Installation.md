---
type: knowledge
project: ivc_ai
topic: installation
tags: [ivc_ai, server-setup, installation, lvm]
created: 2026-11-19
updated: 2026-11-19
---
# 02. Установка Debian 13 (Trixie)

## Подготовка и загрузка
- Образ debian-13.7.0-amd64-netinst.iso (firmware включена). Ventoy: Install на флешку, ISO копировать файлом.
- F8 - пункт с префиксом UEFI. Меню - Install (текстовый). Экран гаснет: e, стрелка вниз x3, End, дописать nomodeset, F10.
- Локаль/раскладка: английский удобнее для поиска ошибок. Hostname латиницей, домен пусто.
- Сеть: DHCP; не удалось - USB-модем ([[06_Network_Fix_USB_Modem]]), повторить автонастройку.

## Учётные записи и ПО
- Пароль root ПУСТО (дважды Продолжить): установщик поставит sudo и добавит пользователя в группу sudo. Все скрипты 07 рассчитаны на это.
- Логин пользователя: строчная латиница.
- Зеркало deb.debian.org, прокси пусто. Сканировать доп. носители - Нет.
- ПО: ТОЛЬКО SSH server + standard system utilities. Десktop и все DE снять.
- GRUB: Да, /dev/nvme0n1 (UEFI сам найдёт ESP). Перезагрузка, флешку вынуть.

## Разметка (Manual)
| # | Устройство | Размер | ФС | Точка |
|---|---|---|---|---|
| 1 | nvme0n1p1 | 1 GiB | FAT32 ESP | /boot/efi |
| 2 | nvme0n1p2 | 2 GiB | ext4 | /boot |
| 3 | nvme0n1p3 | ~830 GiB | LVM PV | - |
| - | vg0/lv_root | 60 GiB | ext4 | / |
| - | vg0/lv_var | 30 GiB | ext4 | /var (reserved 1%) |
| - | vg0/lv_docker | 150 GiB | do not use | - |
| - | vg0/lv_home | 400 GiB | do not use | - |
| - | vg0/lv_swap | 8 GiB | swap | - |
| - | VG свободно | ~182 GiB | резерв | lvextend -r |
| - | неразмечено | ~100 GiB | overprovisioning NVMe | - |

lv_docker и lv_home НЕ форматировать в установщике: это делает Этап Б (07) с mkfs.ext4 -F -m 1 и миграцией старого home в /var/tmp/ivc_home_old. Причина отсрочки - контроль над форматированием и безопасный перенос, а не плотность inode.
/tmp отдельным разделом не делаем: в trixie tmpfs, Этап А маскирует tmp.mount.

## После первой загрузки
Доставить скрипты и публичный ключ с клиента: [[09_Client_File_Delivery]]. Затем Этап А (07).

## Связи
- [[01_BIOS_Preparation]]
- [[06_Network_Fix_USB_Modem]]
- [[07_Automation_Scripts]]
- [[09_Client_File_Delivery]]
- [[10_Walkthrough_Manual]]

