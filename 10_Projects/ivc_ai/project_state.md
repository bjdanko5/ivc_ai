---
created: 2026-11-18
updated: 2026-11-19
tags:
  - knowledge
  - procurement
---

# ivc_ai: статус проекта

## Сейчас
- Vault и сайт-руководство готовы; ожидается поставка железа ([[hardware_procurement]]).
- Руководство: [[07_Automation_Scripts]] (источник правды), [[10_Walkthrough_Manual]] (ручной режим).

## Принятые решения
- 2026-11-19: единственный источник правды по серверу - 20_Knowledge/Server_Setup/docs; корневые дубликаты retired.
- 2026-11-19: модель NanoPlus (12.55 ГБ, полный GPU-offload) вместо MiniPlus Q5_K_M.
- 2026-11-19: SSH двухфазно; пароли отключаются только после подтверждения ключевого входа.
- 2026-11-19: локальный сканер секретов отключён решением владельца; push protection GitHub остаётся.

## Следующие шаги
1. Поставка и сборка.
2. [[01_BIOS_Preparation]] - [[02_Debian_Installation]].
3. [[09_Client_File_Delivery]] - доставка скриптов и ключа.
4. [[07_Automation_Scripts]] Этап А - перезагрузка - Этап Б.
5. [[05_AI_Tools_Setup]] - модель, launcher, эндпоинт; Pi Agent отдельно.

## Связи
- [[vault_map]]
- [[hardware_procurement]]
- [[07_Automation_Scripts]]
- [[10_Walkthrough_Manual]]

