---
type: knowledge
project: ivc_ai
topic: model-card
model: Cyber-Tiel-Coder-35B-A3B-APEX-I-MiniPlus-V2.1-GGUF
created: 2026-11-18
tags: [knowledge, model, coding, local_ai, moe]
---

# Cyber-Tiel-Coder-35B-A3B-APEX-I-MiniPlus-V2.1

## Ссылка

https://huggingface.co/IsValorum/Cyber-Tiel-Coder-35B-A3B-APEX-I-MiniPlus-V2.1-GGUF

## Архитектура

- Тип: MoE (Mixture of Experts)
- Total params: 35B
- Active params: ~3B (при инференсе)
- Контекст: (уточнить на HF)
- Специализация: код, программирование

## Почему эта модель

MoE-архитектура даёт качество 30B+ модели при потреблении ресурсов 7B-модели.
Активируются только нужные эксперты -> высокая скорость на потребительском железе.
Оптимизирована для кодинга.

## Требования к железу (оценка)

| Квантование | Размер файла | VRAM (оценка) | Качество |
|-------------|-------------|---------------|----------|
| Q4_K_M      | ~20 GB      | ~22 GB        | хороший баланс |
| Q5_K_M      | ~24 GB      | ~26 GB        | лучше качество |
| Q6_K        | ~28 GB      | ~30 GB        | близко к FP16 |
| Q8_0        | ~35 GB      | ~37 GB        | почти без потерь |

> Уточнить реальные цифры после тестирования на целевом железе.

## Установка (Ollama)

    ollama pull hf.co/IsValorum/Cyber-Tiel-Coder-35B-A3B-APEX-I-MiniPlus-V2.1-GGUF:Q4_K_M

Если нет в Ollama-реестре — скачать GGUF вручную и создать Modelfile:

    FROM ./Cyber-Tiel-Coder-35B-A3B-Q4_K_M.gguf
    TEMPLATE "{{ .Prompt }}"
    PARAMETER num_ctx 8192

    ollama create cyber-tiel -f Modelfile

## Тестовые промпты для оценки

1. Написать функцию на Python с type hints и docstring.
2. Рефакторинг длинной функции.
3. Объяснить сложный код.
4. Написать unit-тесты.
5. Исправить баг по описанию ошибки.

## Результаты тестирования

Заполнить после получения компьютера:

- Скорость (tokens/s):
- Время до первого токена:
- Качество кода (субъективно):
- Проблемы / ограничения:

## Связанные

- [[hardware_profile]]
- [[model_registry]]
