---
created: 2026-11-19
updated: 2026-11-19
tags:
  - ssh
  - scp
  - windows
  - deployment
---

# Доставка файлов с клиента (Windows) на сервер

## Что где лежит
- Клиент: `C:\Temp\ivc_deploy\` - `setup_part1.sh`, `setup_part2.sh` (LF, UTF-8), приватный ключ `id_ed25519`, публичный `id_ed25519.pub`.
- На сервер едет ТОЛЬКО `.pub` (как `ssh_pubkey_to_add.pub`) и скрипты. Приватный ключ остаётся на клиенте - им клиент доказывает серверу, что он свой.
- Модель и mmproj/mtp сервер качает сам с Hugging Face (Этап Б); по scp они не передаются.

## Вариант 1: встроенный scp (без установки чего-либо)
OpenSSH Client есть в Windows 10 1809+/11. Проверка: `ssh -V`. Если нет: Параметры - Приложения - Дополнительные компоненты - OpenSSH Client (бесплатно).

Ключ (если нет готового; можноreuse существующий `%USERPROFILE%\.ssh\id_ed25519.pub` от GitHub):
```bat
ssh-keygen -t ed25519 -f C:\Temp\ivc_deploy\id_ed25519 -N "" -C "ivc_ai deploy"
```

Первая передача (пока по паролю, ключа на сервере ещё нет):
```bat
scp C:\Temp\ivc_deploy\setup_part1.sh C:\Temp\ivc_deploy\setup_part2.sh user@IP:/var/tmp/
scp C:\Temp\ivc_deploy\id_ed25519.pub user@IP:ssh_pubkey_to_add.pub
```
`/var/tmp` - world-writable (sticky), sudo для scp не нужен. Относительный путь после `:` считается от home пользователя.

Дальше вход по ключу:
```bat
ssh -i C:\Temp\ivc_deploy\id_ed25519 user@IP
```

Чтобы не писать `-i` каждый раз и чтобы VS Code Remote SSH подхватил сервер сам - `%USERPROFILE%\.ssh\config`:
```text
Host ivc-ai
    HostName IP
    User user
    IdentityFile C:\Temp\ivc_deploy\id_ed25519
```
После этого: `scp C:\Temp\ivc_deploy\setup_part1.sh ivc-ai:/var/tmp/`, а в VS Code - Remote-SSH: Connect to Host - ivc-ai.

## CRLF - главная ловушка
bash не переваривает `\r`: скрипт с CRLF падает на первой строке. Генератор пишет LF; если правили в Блокноте - на сервере:
```bash
sed -i 's/\r$//' /var/tmp/setup_part1.sh /var/tmp/setup_part2.sh
```

## Вариант 2: WinSCP (GUI, бесплатно)
1. winscp.net -下载安装 не нужен, portable-версия подойдёт.
2. New Session: протокол SFTP, Host = IP, User = user, пароль (пока ключ не установлен).
3. Advanced - SSH - Authentication - Private key: выбрать `id_ed25519`; WinSCP сам конвертирует OpenSSH-ключ в .ppk.
4. Перетащить `setup_part*.sh` в `/var/tmp/`, `id_ed25519.pub` в home с переименованием в `ssh_pubkey_to_add.pub`.
5. Режим передачи для .sh - Binary (чтобы не получить CRLF).

## Если у сервера нет LAN (Realtek не поднялся)
scp с клиента не дойдёт: USB-модем даёт серверу адрес в подсети телефона, клиент туда не маршрутизируется. Варианты: USB-Ethernet адаптер; либо флешка со скриптами (mount /mnt, cp в /var/tmp); либо paste через nano с консоли. После лечения NIC (firmware-realtek / backports-ядро, см. 07) scp работает штатно.

## Права после доставки
Скрипты запускаются как `sudo bash /var/tmp/setup_partN.sh` - chmod +x не требуется. Ключ на сервере раскладывается по местам самими скриптами (Этап А шаг 4, Этап Б шаг 3).

## Связи
- [[07_Automation_Scripts]]
- [[06_Network_Fix_USB_Modem]]
- [[03_System_Configuration]]
