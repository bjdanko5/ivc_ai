---
created: 2026-11-19
updated: 2026-11-19
tags:
  - server-setup
---

# 03. Базовая настройка системы (соответствие 07)

Источник правды - [[07_Automation_Scripts]]. Ручные команды по шагам - [[10_Walkthrough_Manual]].

## Сетевая идентичность
- DHCP оставлен; аренду закрепить на роутере (07, финал Этапа Б печатает IP).
- Статика не обязательна; если нужна - /etc/network/interfaces, но тогда обновить ssh-config на клиенте.

## SSH: двухфазная политика
- Фаза 1 (Этап А): openssh-server + firmware-realtek, KillMode=process (upgrade не убивает сессию), публичный ключ добавляется, пароли ещё включены.
- Фаза 2 (Этап Б, после миграции home): подтверждение ключевого входа в новом окне, затем drop-in /etc/ssh/sshd_config.d/99-ivc-hardening.conf (PasswordAuthentication no, KbdInteractiveAuthentication no, PubkeyAuthentication yes), правка основного sshd_config, sshd -t, reload, TCP-проверка.
- Бэкап sshd_config создаётся перед правкой.

## Каталоги
- ~/src ~/downloads ~/models ~/projects - на lv_home (400 ГБ).
- /opt/ivc_ai/pi и /opt/ivc_ai/logs - реальные; /opt/ivc_ai/models и /opt/ivc_ai/llama.cpp - симлинки в home (07, Этап Б шаг 5).

## Память и диск
- zram: min(ram/2, 32768) MiB, zstd; приоритет выше дискового swap lv_swap 8 GiB.
- sysctl: vm.swappiness=100, vm.page-cluster=0 (/etc/sysctl.d/99-ivc-ai.conf).
- fstrim.timer включён (Kingston NV3 QLC без DRAM).
- /tmp: tmp.mount замаскирован на Этапе А, после перезагрузки /tmp на диске.

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

