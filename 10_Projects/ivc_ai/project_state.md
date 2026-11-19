---
type: project
project: ivc_ai
created: 2026-11-19
updated: 2026-11-19
---

# ivc_ai: статус проекта

## Сейчас
- Vault, сайт и руководство готовы; ожидается поставка железа ([[hardware_procurement]]).
- Руководство: [[07_Automation_Scripts]] (SSOT), [[10_Walkthrough_Manual]] (ручной режим).
- Эксплуатация: [[site_ops]], [[chat_playbook]], [[vault_map]], [[ai_chat_rules]].

## Принятые решения
- 2026-11-19: SSOT по серверу - docs; корневые дубликаты retired (бэкап C:\Temp\ivc_retired_backup).
- 2026-11-19: модель NanoPlus (12.55 ГБ, полный GPU-offload) вместо MiniPlus Q5_K_M.
- 2026-11-19: SSH двухфазно; пароли off только после подтверждения ключевого входа.
- 2026-11-19: сканер секретов отключён владельцем; отчёты scan_*.json не пишутся.
- 2026-11-19: единая схема frontmatter + топиковые теги (models и др.).
- 2026-11-19: лаунчер сайта постоянный - tools/run_wiki_lan.py.

- 2026-11-19: механика автосинхронизации описана в sync_ops (факты обнаружены скриптом).

## Следующие шаги
1. Поставка и сборка.
2. [[01_BIOS_Preparation]] - [[02_Debian_Installation]].
3. [[09_Client_File_Delivery]].
4. [[07_Automation_Scripts]] Этап А - reboot - Этап Б.
5. [[05_AI_Tools_Setup]]; Pi Agent отдельно.

## Связи
- [[vault_map]]
- [[sync_ops]]
- [[site_ops]]
- [[chat_playbook]]
- [[hardware_procurement]]
- [[07_Automation_Scripts]]

