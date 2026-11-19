---
type: knowledge
project: ivc_ai
topic: nvidia
tags: [ivc_ai, server-setup, nvidia, cuda]
created: 2026-11-19
updated: 2026-11-19
---
# 04. Драйверы NVIDIA и CUDA (соответствие 07)

## Предпосылки
- Secure Boot выключен ([[01_BIOS_Preparation]]): DKMS-модули не подписаны.
- Репозиторий: developer.download.nvidia.com/compute/cuda/repos/debian13/x86_64 (cuda-keyring_1.1-1_all.deb).

## Пакеты (Этап А)
- nvidia-driver-pinning-620 - фиксирует ветку драйвера. Если пакета нет: apt-cache search '^nvidia-driver-pinning' и выбрать доступную ветку.
- nvidia-driver-cuda + nvidia-kernel-open-dkms - compute-only драйвер (без X11).
- cuda-toolkit - nvcc и библиотеки ИЗ ЭТОГО ЖЕ репозитория.

## Почему не Debian nvidia-cuda-toolkit
- Debian-овский toolkit 12.x не знает sm_120 (Blackwell) и конфликтует с pinned-драйвером 620.
- nvcc лежит в /usr/local/cuda/bin и НЕ в PATH: сборка llama.cpp экспортирует PATH явно (07, Этап Б шаг 10).

## Проверки
```bash
nvidia-smi
/usr/local/cuda/bin/nvcc --version
dkms status
```
- nvidia-smi не работает после перезагрузки: смотреть Secure Boot и dkms status; журнал этапа - /var/log/ivc_ai_setup.log.

## GPU в Docker
nvidia-container-toolkit из репозитория libnvidia-container (ключ .asc, без gnupg), nvidia-ctk runtime configure --runtime=docker (07, Этап Б шаг 8).

## Связи
- [[01_BIOS_Preparation]]
- [[07_Automation_Scripts]]
- [[05_AI_Tools_Setup]]
- [[10_Walkthrough_Manual]]

