---
created: 2026-11-19
updated: 2026-11-19
tags:
  - server-setup
---

# 09. Доставка файлов с клиента (Windows)

## Что где лежит
- Клиент: C:\Temp\ivc_deploy\ - setup_part1.sh, setup_part2.sh (LF, UTF-8), id_ed25519 (приватный), id_ed25519.pub.
- На сервер едет только .pub (как ssh_pubkey_to_add.pub) и скрипты. Приватный ключ остаётся на клиенте.
- Модель/mmproj/mtp сервер качает сам с HF (Этап Б); по scp не передаются.

## Вариант 1: встроенный scp
OpenSSH Client есть в Windows 10 1809+/11: проверка ssh -V. Нет - Дополнительные компоненты - OpenSSH Client (бесплатно).
Ключ (или reuse готового %USERPROFILE%\.ssh\id_ed25519.pub):
```bat
ssh-keygen -t ed25519 -f C:\Temp\ivc_deploy\id_ed25519 -N "" -C "ivc_ai deploy"
```
Первая передача (по паролю, ключа на сервере ещё нет):
```bat
scp C:\Temp\ivc_deploy\setup_part1.sh C:\Temp\ivc_deploy\setup_part2.sh user@IP:/var/tmp/
scp C:\Temp\ivc_deploy\id_ed25519.pub user@IP:ssh_pubkey_to_add.pub
```
/var/tmp - world-writable (sticky), sudo не нужен. Путь после : относительный - от home.
Дальше: ssh -i C:\Temp\ivc_deploy\id_ed25519 user@IP.

Чтобы не писать -i и чтобы VS Code Remote SSH подхватил сам - %USERPROFILE%\.ssh\config:
```text
Host ivc-ai
    HostName IP
    User user
    IdentityFile C:\Temp\ivc_deploy\id_ed25519
```
Тогда scp ... ivc-ai:/var/tmp/ и VS Code - Remote-SSH - ivc-ai.

## CRLF - главная ловушка
bash падает на \r. Генератор пишет LF; если правили в Блокноте - на сервере:
```bash
sed -i 's/\r$//' /var/tmp/setup_part1.sh /var/tmp/setup_part2.sh
```

## Вариант 2: WinSCP (GUI, бесплатно)
1. winscp.net, установка не нужна - portable подойдёт.
2. New Session: SFTP, Host=IP, User=user, пароль (пока ключ не установлен).
3. Advanced - SSH - Authentication - Private key: id_ed25519; WinSCP сам конвертирует в .ppk.
4. setup_part*.sh в /var/tmp/, id_ed25519.pub в home как ssh_pubkey_to_add.pub.
5. Режим передачи для .sh - Binary.

## Если у сервера нет LAN
USB-модем даёт адрес в подсети телефона - клиент не маршрутизируется, scp не дойдёт. Варианты: USB-Ethernet; флешка (mount /mnt, cp в /var/tmp); nano-paste с консоли. После лечения NIC (06) scp работает штатно.

## Права и фазы SSH
Запуск sudo bash /var/tmp/setup_partN.sh, chmod +x не нужен. Ключ раскладывается Этапом А (шаг 4); пароли отключаются Этапом Б (шаг 3) только после подтверждения ключевого входа в новом окне.

## Связи
- [[07_Automation_Scripts]]
- [[06_Network_Fix_USB_Modem]]
- [[03_System_Configuration]]
- [[10_Walkthrough_Manual]]

