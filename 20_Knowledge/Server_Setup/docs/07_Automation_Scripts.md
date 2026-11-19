---
created: 2026-11-19
tags:
  - automation
  - bash
  - nvidia
  - docker
---

# Скрипты автоматизации настройки сервера

## Этап А: До первой перезагрузки
Запускается сразу после установки системы. Устанавливает драйвер NVIDIA (ветка 620) и обновляет репозитории.

```bash
# Сохранить как setup_part1.sh и запустить: bash setup_part1.sh
# (Код скрипта см. в источнике или в tools/scripts/)
```

## Этап Б: После перезагрузки
Форматирует LVM-тома (`lv_docker`, `lv_home`), настраивает Docker, zram, Node.js, pnpm, uv и собирает llama.cpp.

**Внимание:** Этот скрипт удаляет данные на томах Docker и Home!

```bash
# Сохранить как setup_part2.sh и запустить: bash setup_part2.sh
```

## Ключевые компоненты
- **NVIDIA Driver:** Compute-only, ветка 620+ для RTX 5070 Ti.
- **Docker:** Настроен с ограничением логов и поддержкой GPU (libnvidia-container).
- **Языки:** Node.js (LTS через nvm), pnpm, uv.
- **AI:** llama.cpp со сборкой под CUDA arch 120 (Blackwell).

## Связи
- [[Debian_Server_Setup]]
- [[04_NVIDIA_Drivers]]
- [[05_AI_Tools_Setup]]
- [[06_Network_Fix_USB_Modem]]
