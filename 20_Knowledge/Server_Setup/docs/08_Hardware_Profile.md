---
type: knowledge
project: ivc_ai
topic: hardware
tags: [ivc_ai, server-setup, hardware, models]
created: 2026-11-19
updated: 2026-11-19
---
# 08. Hardware Profile (ivc_ai)

Закупка оформлена, ожидается поставка. Состав и статус - [[hardware_procurement]] (вне этой папки).

## Спецификация
| Компонент | Модель | Ключевой параметр |
|---|---|---|
| CPU | AMD Ryzen 9 9900X BOX | 12C/24T, Zen 5, AVX-512 |
| RAM | Silicon Power Xpower Zenith 64 GB DDR5 | UDIMM |
| GPU | ASUS RTX 5070 Ti PRIME OC | 16 GB GDDR7 |
| Storage | Kingston NV3 1 TB NVMe | QLC, DRAM-less, 320 TBW |
| PSU | DeepCool GamerStorm PN1000D | 1000W ATX 3.x |
| MB | ASUS PRIME B850-PLUS-CSM | AM5 |
| Cooler | Arctic Freezer 36-S | воздух |
| Case | Chieftec Night Hunter | ATX |

## Совместимость с моделями (исправлено по 07)
Основной выбор: NanoPlus (~12.55 ГБ) - помещается в 16 ГБ VRAM целиком вместе с mmproj и mtp; длинный ctx ограничивается KV, launcher подбирает конфигурацию (05, 07).

MiniPlus-V2.1 (legacy, не используется): веса Q4_K_M ~20 ГБ, Q5_K_M ~24 ГБ, Q6_K ~28 ГБ, Q8_0 ~35 ГБ. Все больше 16 ГБ VRAM, полный GPU-offload невозможен; только hybrid (часть слоёв/experts в RAM). Прежняя таблица 'VRAM 6-16 GB, влезает' была ошибочной оценкой и удалена.

CPU offload как резерв: 64 GB DDR5 + 12C позволяют hybrid без катастрофы по скорости; ориентир 5-10 t/s против 30-50 t/s на чистом GPU.

## Storage
OS+софт ~100 ГБ (lv_root 60 + lv_var 30), модели NanoPlus ~14 ГБ, Docker отдельно 150 ГБ, home 400 ГБ, VG-резерв ~182 ГБ, неразмечено ~100 ГБ под overprovisioning. Второй NVMe при необходимости (B850 имеет несколько M.2).

## Структура на сервере
/opt/ivc_ai/models и /opt/ivc_ai/llama.cpp - симлинки в ~/models и ~/src/llama.cpp; /opt/ivc_ai/pi и /opt/ivc_ai/logs - реальные каталоги (07).

## Связи
- [[07_Automation_Scripts]]
- [[05_AI_Tools_Setup]]
- [[11_Memory_and_Zram]]
- [[02_Debian_Installation]]
- [[10_Walkthrough_Manual]]

