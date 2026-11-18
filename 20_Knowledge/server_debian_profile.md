---
type: knowledge
project: ivc_ai
topic: server-profile
os: debian
created: 2026-11-18
tags: [knowledge, server, debian, local_ai]
---

# Серверный профиль (Debian + llama.cpp)

## Назначение

Linux-сервер для инференса моделей. Клиент (Windows + VS Code) подключается по SSH.

## Железо

| Компонент | Модель | Параметр |
|-----------|--------|----------|
| CPU | AMD Ryzen 9 9900X | 12C/24T, Zen 5, AVX-512 |
| RAM | Silicon Power Xpower Zenith 64 GB DDR5 | UDIMM |
| GPU | ASUS RTX 5070 Ti PRIME OC | 16 GB GDDR7 |
| Storage | Kingston NV3 1 TB NVMe | M.2 |
| PSU | DeepCool PN1000D | 1000W |
| MB | ASUS PRIME B850-PLUS-CSM | AM5 |

## ОС и софт

- ОС: Debian (stable/testing)
- Драйвер: NVIDIA proprietary + CUDA Toolkit 12.x
- Инференс: llama.cpp (собран с GGML_CUDA=ON)
- Модель: Cyber-Tiel-Coder-35B-A3B-APEX-I-MiniPlus-V2.1-GGUF
- Агент: Pi Agent v1.5.2

## Почему Debian, а не Windows

- Нативная поддержка CUDA без WSL-overhead
- Меньше фонового потребления RAM/VRAM
- Стабильный long-running сервер для llama-server
- Pi Agent и llama.cpp — native Linux binaries

## Структура на сервере

    /opt/ivc_ai/
    ├── models/           # GGUF-файлы моделей
    ├── llama.cpp/        # собранная llama.cpp
    ├── pi/               # Pi Agent config + extensions
    └── logs/             # логи инференса

    ~/projects/           # рабочие репозитории (доступны через SSH)

## Связанные

- [[hardware_profile]]
- [[ssh_remote_setup]]
- [[pi_agent_config]]
- [[llamacpp_platform]]
