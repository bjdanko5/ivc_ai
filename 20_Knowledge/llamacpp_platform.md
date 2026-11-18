---
type: knowledge
project: ivc_ai
topic: llamacpp-platform
created: 2026-11-18
tags: [knowledge, llamacpp, platform, local_ai]
---

# Платформа запуска llama.cpp (ivc_ai)

## Железо

- GPU: ASUS RTX 5070 Ti 16 GB GDDR7
- CPU: AMD Ryzen 9 9900X (12C/24T, Zen 5, AVX-512)
- RAM: 64 GB DDR5
- Storage: Kingston NV3 1 TB NVMe

## Установка (Windows + CUDA)

### Вариант 1: Prebuilt (рекомендуемый старт)

Скачать последний release с поддержкой CUDA:

    https://github.com/ggerganov/llama.cpp/releases

Выбрать: llama-bXXXX-bin-win-cuda-cu12.x-x64.zip

Распаковать в C:\ivc_ai\tools\llama.cpp\

### Вариант 2: Сборка из исходников (для максимальной оптимизации под 9900X)

Требования: Visual Studio 2022 + CUDA Toolkit 12.x + CMake

    git clone https://github.com/ggerganov/llama.cpp.git
    cd llama.cpp
    cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=120
    cmake --build build --config Release -j24

> -DCMAKE_CUDA_ARCHITECTURES=120 — архитектура Blackwell (RTX 50xx).
> Уточнить точное значение в документации NVIDIA при выходе драйверов.
> Если не поддерживается — использовать 89 (Ada Lovelace fallback).

## Запуск Cyber-Tiel-Coder-35B-A3B

### Базовый запуск (интерактивный чат)

    llama-cli.exe ^
      -m C:\models\Cyber-Tiel-Coder-35B-A3B-Q5_K_M.gguf ^
      -ngl 99 ^
      -c 8192 ^
      -t 12 ^
      --chat-template chatml ^
      -cnv

Параметры для RTX 5070 Ti 16 GB:

| Параметр | Значение | Пояснение |
|----------|---------|-----------|
| -ngl     | 99      | Все слои на GPU (MoE ~3B active влезает в 16 GB) |
| -c       | 8192    | Контекст. При Q5_K_M + 8K остаётся ~6 GB VRAM под KV-cache |
| -t       | 12      | Потоки CPU = физическим ядрам 9900X |
| -fa      | (флаг)  | Flash Attention — включить если доступно в сборке |
| -ctk/q   | q8_0    | Квантование KV-cache для экономии VRAM при длинном контексте |

### Для агентского кодинга (non-interactive, JSON output)

    llama-cli.exe ^
      -m C:\models\Cyber-Tiel-Coder-35B-A3B-Q5_K_M.gguf ^
      -ngl 99 -c 8192 -t 12 ^
      --chat-template chatml ^
      -p "SYSTEM: You are a coding agent..." ^
      --json-schema '{"type":"object","properties":{"code":{"type":"string"}}}' ^
      -n 2048 --no-display-prompt

### Бенчмарк скорости

    llama-bench.exe ^
      -m C:\models\Cyber-Tiel-Coder-35B-A3B-Q5_K_M.gguf ^
      -ngl 99 -c 4096 -t 12 ^
      -p 512 -n 128 -r 3

Ожидаемые результаты (оценка):

| Режим | Скорость (t/s) | Примечание |
|-------|---------------|------------|
| Pure GPU (Q5_K_M) | 40-60 | Все слои в VRAM |
| Partial offload (Q8_0) | 8-15 | Часть слоёв в RAM |
| Prompt processing | 200-400 t/s | Зависит от длины промпта |

## Интеграция с Ollama (рекомендуемый workflow)

llama.cpp — низкоуровневый инструмент. Для повседневной работы удобнее Ollama:

    ollama serve

Ollama использует llama.cpp внутри, но добавляет:
- Автоматическую загрузку моделей
- REST API (localhost:11434)
- Совместимость с Continue.dev, AnythingLLM, Khoj

Для кастомных GGUF создать Modelfile:

    FROM ./Cyber-Tiel-Coder-35B-A3B-Q5_K_M.gguf
    TEMPLATE "{{ .Prompt }}"
    PARAMETER num_ctx 8192
    PARAMETER num_gpu 99

    ollama create cyber-tiel -f Modelfile

## Мониторинг ресурсов

Во время инференса следить за VRAM:

    nvidia-smi -l 1

Или через nvtop / GPU-Z.

Критические пороги для RTX 5070 Ti 16 GB:
- VRAM > 15 GB: риск OOM, уменьшить -c или перейти на Q4_K_M
- RAM > 55 GB: проверить утечки, уменьшить batch size
- GPU temp > 85°C: проверить охлаждение (Arctic Freezer 36-S должен справляться)

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| CUDA not found | Проверить CUDA Toolkit, переустановить prebuilt с правильной версией cu |
| OOM при -c 8192 | Уменьшить до 4096 или использовать -ctk q4_0 |
| Медленный prompt processing | Включить -fa (Flash Attention), проверить что все слои на GPU (-ngl 99) |
| Неверный вывод | Проверить --chat-template, скачать правильный GGUF variant |
| AVX-512 не используется | Собрать из исходников с -DGGML_AVX512=ON |

## Связанные

- [[model_cyber_tiel_coder]]
- [[hardware_profile]]
- [[local_ai_stack]]
