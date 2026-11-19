---
created: 2026-11-19
tags:
  - nvidia
  - cuda
  - drivers
---

# Часть 4: Драйверы NVIDIA (RTX 5070 Ti)

## 4.1. Выбор драйвера
- Использовать open-kernel модули ветки **620+** или проприетарные драйверы с сайта NVIDIA для поддержки архитектуры Blackwell (sm_120).
- Режим: **Compute-only** (без X11/Wayland).

## 4.2. Установка CUDA Toolkit
- Версия: **CUDA 13.5** (или актуальная для Trixie).
- Добавить репозиторий NVIDIA и установить `nvidia-cuda-toolkit`.

## 4.3. Проверка
```bash
nvidia-smi
nvcc --version
```

## Связи
- [[Debian_Server_Setup]]
- [[03_System_Configuration]]
- [[Local AI Setup]]
