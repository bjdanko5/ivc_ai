---
type: knowledge
project: ivc_ai
topic: memory
tags: [ivc_ai, server-setup, memory, zram, swap]
created: 2026-11-19
updated: 2026-11-19
---

# 11. Память и zram: зачем и как настроено

zram - swap, который живёт не на диске, а в сжатом виде в RAM. Ядро вытесняет холодные страницы памяти в сжатый блок /dev/zram0 (zstd), а не пишет их на NVMe.
Настройка выполняется Этапом Б (шаг 6) в [[07_Automation_Scripts]]; ручной эквивалент - блок 5E в [[10_Walkthrough_Manual]]. Политика памяти описана в [[03_System_Configuration]].

## Зачем на этом сервере
1. Страховка от OOM при пиках: cmake --build -j24 llama.cpp (каждый nvcc - несколько ГБ), попытка KV-cache на 262144 контекста, Docker-сборка + Qdrant + pnpm install одновременно. Без swap ядро убьёт llama-server или контейнер; с zram пик переживается.
2. Защита QLC-диска: Kingston NV3 - QLC без DRAM-буфера, 320 TBW. Swap - мелкие случайные записи, худший режим для QLC (усиление записи, исчерпание SLC-кэша, износ). zram убирает этот трафик с диска; ради этого же оставлено ~100 ГБ неразмеченными и включён fstrim ([[08_Hardware_Profile]], [[02_Debian_Installation]]).
3. Скорость вместо thrashing: zstd на Zen 5 - гигабайты в секунду, задержки микросекунды; swap на NVMe - миллисекунды и очередь I/O. Под нагрузкой SSH остаётся отзывчивым.

## Почему параметры именно такие
| Параметр | Причина |
|---|---|
| zram-size = min(ram / 2, 32768) | Устройство на 32 GiB, реально занимает ~1/2-1/3 этого в RAM (сжатие). Потолок не даёт zram самому съесть память при несжимаемых данных |
| compression-algorithm = zstd | Лучшее соотношение скорость/степень сжатия на CPU; на 12 ядрах цена незаметна |
| vm.swappiness=100 | Вытеснять anon-память в zram дёшево, поэтому ядру выгоднее отдать холодные кучи процессов в zram, чем выбрасывать page cache - а в page cache лежат mmap-нутые веса GGUF. Выбросишь кэш - модель начнёт перечитываться с NVMe |
| vm.page-cluster=0 | Отключает swap-readahead: с диска читать пачкой выгодно, из zram - лишняя декомпрессия и задержка. По одной странице |
| приоритет zram (100) > lv_swap (8 GiB) | zram - первый эшелон; дисковый swap - холодный резерв, когда сжатие уже не спасает. Гибернации нет, 8 GiB достаточно |

## Чего zram НЕ делает
- Не добавляет RAM и не помогает VRAM: память GPU отдельная, длинный контекст решает ctx-fallback в launcher ([[05_AI_Tools_Setup]]).
- Не ускоряет инференс сам по себе; делает так, чтобы сервер не падал и не тормозил в моменты пиков.

## Проверка
```bash
swapon --show        # zram0 с приоритетом 100, lv_swap ниже
zramctl              # DATA (orig) против COMPR (сжато)
free -h              # Swap used обычно 0 или немного в пиках
```
- COMPR заметно меньше DATA - сжатие работает как задумано.
- Swap used постоянно растёт до потолка - сигнал, что нагрузке реально не хватает RAM, а не проблема настройки.
- Юнит: systemctl status systemd-zram-setup@zram0; конфиг /etc/systemd/zram-generator.conf; sysctl /etc/sysctl.d/99-ivc-ai.conf.

## Связи
- [[07_Automation_Scripts]]
- [[10_Walkthrough_Manual]]
- [[03_System_Configuration]]
- [[08_Hardware_Profile]]
- [[05_AI_Tools_Setup]]
- [[02_Debian_Installation]]

