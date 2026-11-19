---
created: 2026-11-19
updated: 2026-11-19
tags:
  - server-setup
---

# 01. BIOS (ASUS PRIME B850-PLUS-CSM)

## Прошивка
- Версия 1804 (21.09.2026), AGESA ComboAM5 PI 1.3.0.1d; в 1644 исправлены boot/stability issues Ryzen 9000.
- Флешка FAT32, MBR, один раздел, от 1 ГБ. Файл переименовать в A5659.CAP (BIOSRenamer.exe или вручную), в корень.
- FlashBack: система выключена, 24-pin подключён, БП включён; флешка в USB 2.0 порт №5 (BIOS FlashBack); кнопку держать 3 с до трёх миганий; ждать до 8 мин.
- Мигнул 5 с и горит ровно = неверный формат/имя. Не вынимать флешку и не снимать питание в процессе.
- Вход: Delete/F2, затем F7 (Advanced Mode). Проверить версию на Main.

## Настройки
- Secure Boot: Boot - Secure Boot - OS Type = Other OS (выключен). ОБЯЗАТЕЛЬНО: иначе DKMS-модули NVIDIA (07, Этап А) не загрузятся.
- CSM: Launch CSM = Disabled (иначе не включится Re-Size BAR).
- PCIe: Above 4G Decoding = Enabled, затем Re-Size BAR Support = Enabled.
- Armoury Crate: Download & Install = Disabled.
- Fast Boot: Disabled (успеть нажать Delete).
- EXPO: пока Auto. Включать только после проверки стабильности; при проблемах сброс CLRTC 5-10 с при снятом питании.
- F10 сохранить.

## Связи
- [[02_Debian_Installation]]
- [[07_Automation_Scripts]]
- [[08_Hardware_Profile]]
- [[10_Walkthrough_Manual]]

