---
type: knowledge
project: ivc_ai
topic: models
tags: [ivc_ai, server-setup, models, ai, llama]
created: 2026-11-19
updated: 2026-11-19
---
# 05. Инструменты ИИ (соответствие 07)

## Модель: NanoPlus
Репозиторий IsValorum/Cyber-Tiel-Coder-35B-A3B-APEX-I-NanoPlus-GGUF. Четыре файла:
| Файл | Назначение |
|---|---|
| Cyber-Tiel-Coder-35B-A3B.APEX-I-NanoPlus.gguf (~12.55 ГБ) | основные веса, влезают в 16 ГБ VRAM целиком |
| mmproj-Q8_0.gguf | vision-проектор (--mmproj) |
| mtp-Cyber-Tiel-Coder-35B-A3B.gguf | draft для speculative decoding (-md, --spec-type draft-mtp) |
| chat_template.jinja | hardened agent-шаблон (--chat-template-file, reasoning_effort medium) |

## llama.cpp
- Исходники ~/src/llama.cpp, симлинк /opt/ivc_ai/llama.cpp.
- Сборка: cmake -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=120; нужен libcurl4-openssl-dev (Этап А).
- Бинарники build/bin/llama-cli, llama-server, llama-bench.

## Launcher и юнит
- /opt/ivc_ai/run-llama-server.sh: -ngl 99 (полный offload не нужен), --jinja, sampling для кода (repeat-penalty 1.0, presence/frequency 0.0, temp 0.6, top-p 0.95, top-k 20, min-p 0).
- ctx 262144 - зона риска по KV: цепочка 262144/f16 - 262144/q8_0 - 131072/q8_0 - 65536/q8_0, выбранная конфигурация логируется.
- Флаги --reasoning-effort / --spec-type проверяются по --help; при отсутствии - fallback без падения.
- llama-server.service: User=обычный пользователь, ConditionPathExistsGlob=/opt/ivc_ai/models/*.gguf, Restart=on-failure.
- Health: curl http://127.0.0.1:8080/health. Клиент: ssh -L 8080:127.0.0.1:8080 user@IP.

## Pi Agent
v1.5.2 устанавливается пользователем ОТДЕЛЬНО, вне 07. Каталог /opt/ivc_ai/pi подготовлен.

## Эмбеддинги
bge-m3 FP16 (~2 ГБ) - отложено: бюджет VRAM занят весами+mmproj+mtp+KV. Возвращаться после замеров фактического потребления.

## Связи
- [[04_NVIDIA_Drivers]]
- [[07_Automation_Scripts]]
- [[08_Hardware_Profile]]
- [[11_Memory_and_Zram]]
- [[10_Walkthrough_Manual]]

