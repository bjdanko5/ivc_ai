---
created: 2026-11-19
tags:
  - bios
  - hardware
  - asus
---

# Часть 1: Настройка BIOS (ASUS PRIME B850-PLUS-CSM)

## 1.1. Прошивка BIOS
- **Модель:** PRIME B850-PLUS-CSM
- **Версия:** 1804 (AGESA ComboAM5 PI 1.3.0.1d)
- **Имя файла:** `A5659.CAP` (обязательно переименовать через `BIOSRenamer.exe`)
- **Метод:** ASUS FlashBack (USB 2.0 порт №5, держать кнопку 3 сек)

## 1.2. Ключевые настройки
1. **Secure Boot:** `Boot` → `Secure Boot` → `OS Type` = `Other OS`
2. **CSM:** `Boot` → `Launch CSM` = `Disabled` (требуется для Re-Size BAR)
3. **PCIe:** `Advanced` → `Above 4G Decoding` = `Enabled`, `Re-Size BAR Support` = `Enabled`
4. **Armoury Crate:** `Tool` → `Download & Install ARMOURY CRATE app` = `Disabled`
5. **Fast Boot:** `Disabled` (для возможности входа в BIOS по Delete)

## 1.3. Память (EXPO)
- Пока оставить `Auto`. Включать EXPO только после проверки стабильности системы.

## Связи
- [[Debian_Server_Setup]]
- [[Hardware Specs]]
