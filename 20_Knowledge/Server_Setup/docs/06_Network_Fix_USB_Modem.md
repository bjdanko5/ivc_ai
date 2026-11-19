---
type: knowledge
project: ivc_ai
topic: network
tags: [ivc_ai, server-setup, network, troubleshooting]
created: 2026-11-19
updated: 2026-11-19
---
# 06. Экстренная сеть: USB-модем и Realtek

## Когда
- Установщик: DHCP не удалась (02, шаг сети).
- После установки: нет линка/адреса на встроенной Realtek RTL8125D (ревизия 0x689 может не поддерживаться ядром 6.12).

## Модем (Android)
1. Кабель USB, мобильный интернет включён, Настройки - Точка доступа - USB-модем.
2. Появляется интерфейс enx... или usb0.
```bash
ip -br link
sudo ip link set enxXXXXXXXXXXXX up
sudo dhclient -v enxXXXXXXXXXXXX
ping -c 3 8.8.8.8
```
- dhclient отсутствует: добавить в /etc/network/interfaces строки allow-hotplug enx... и iface enx... inet dhcp, затем sudo ifup enx....
- В установщике: подключить модем и нажать Повторить автоматическую настройку.

## Лечение встроенной NIC
- Этап А (07) ставит firmware-realtek и печатает диагностику ip -br link / lspci -nnk.
- Если линка нет - ядро из backports (DKMS пересоберёт NVIDIA сам):
```bash
echo 'deb http://deb.debian.org/debian trixie-backports main contrib non-free non-free-firmware' > /etc/apt/sources.list.d/backports.list
apt-get update
apt-get -t trixie-backports install -y linux-image-amd64 linux-headers-amd64
reboot
```

## Важно
Модем - костыль: сервер получает адрес в подсети телефона, клиент с LAN туда не маршрутизируется, scp не дойдёт ([[09_Client_File_Delivery]]. Сняв телефон, сервер потеряет сеть - лечить NIC обязательно.

## Связи
- [[02_Debian_Installation]]
- [[07_Automation_Scripts]]
- [[09_Client_File_Delivery]]
- [[10_Walkthrough_Manual]]

