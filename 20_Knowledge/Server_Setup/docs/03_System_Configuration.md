---
type: knowledge
project: ivc_ai
topic: system
tags: [ivc_ai, server-setup, system, ssh, network]
created: 2026-11-18
updated: 2026-11-19
---
# 03. Базовая настройка системы (соответствие 07)

Источник правды - [[07_Automation_Scripts]]
- [[11_Memory_and_Zram]]. Ручные команды по шагам - [[10_Walkthrough_Manual]].

## Почему Debian, а не Windows
- Нативная CUDA без WSL-overhead.
- Меньше фонового потребления RAM/VRAM.
- Стабильный long-running llama-server.
- llama.cpp и агенты - native Linux binaries.

## Сетевая идентичность
- DHCP оставлен; аренду закрепить на роутере (07, финал Этапа Б печатает IP).
- Статика не обязательна; если нужна - /etc/network/interfaces, тогда обновить ssh-config на клиенте.

## SSH: двухфазная политика
- Фаза 1 (Этап А): openssh-server + firmware-realtek, KillMode=process, ключ добавляется, пароли ещё включены.
- Фаза 2 (Этап Б, после миграции home): подтверждение ключевого входа в новом окне, drop-in 99-ivc-hardening.conf, правка sshd_config, sshd -t, reload, TCP-проверка.
- Бэкап sshd_config перед правкой.

## Каталоги
- ~/src ~/downloads ~/models ~/projects - на lv_home (400 ГБ).
- /opt/ivc_ai/pi и /opt/ivc_ai/logs - реальные; models и llama.cpp - симлинки в home (07, Этап Б шаг 5).

## Память и диск
- zram min(ram/2, 32768) MiB, zstd; приоритет выше lv_swap 8 GiB.
- vm.swappiness=100, vm.page-cluster=0.
- fstrim.timer включён (NV3 QLC без DRAM).
- /tmp: tmp.mount замаскирован, после перезагрузки на диске.

## Диагностика
```bash
ip -br addr
swapon --show
systemctl status ssh --no-pager
findmnt /home /var/lib/docker
```

## Связи
- [[07_Automation_Scripts]]
- [[06_Network_Fix_USB_Modem]]
- [[09_Client_File_Delivery]]
- [[10_Walkthrough_Manual]]
- [[08_Hardware_Profile]]

