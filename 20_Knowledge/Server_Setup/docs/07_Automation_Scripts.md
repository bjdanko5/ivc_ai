---
created: 2026-11-19
updated: 2026-11-19
tags:
  - automation
  - bash
  - nvidia
  - docker
---

# Скрипты автоматизации настройки сервера

**Запускать из /var/tmp** (не из /home — он перемонтируется в процессе):
1. Сохранить скрипты: `nano /var/tmp/setup_part1.sh` и `nano /var/tmp/setup_part2.sh`
2. Этап А: `sudo bash /var/tmp/setup_part1.sh` (в конце — перезагрузка)
3. Положить публичный SSH-ключ в `~/ssh_pubkey_to_add.pub`
4. Этап Б: `sudo bash /var/tmp/setup_part2.sh`

Лог обоих этапов: `/var/log/ivc_ai_setup.log`. При ошибке скрипт останавливается и печатает номер строки.

## Этап А: до первой перезагрузки
Сеть проверяется через apt (HTTP). ca-certificates/curl/wget ставятся ДО любого HTTPS. Драйвер pinned-ветки 620 + CUDA Toolkit (nvcc) из NVIDIA-репо.

```bash
#!/bin/bash
set -Eeuo pipefail
trap 'echo "[!] ОШИБКА: строка $LINENO, код $?" >&2' ERR
exec > >(tee -a /var/log/ivc_ai_setup.log) 2>&1
export DEBIAN_FRONTEND=noninteractive
cd /
echo "=== ЭТАП А: $(date) ==="

if [ "$EUID" -ne 0 ]; then echo "[!] Запустите: sudo bash /var/tmp/setup_part1.sh"; exit 1; fi

REAL_USER="${SUDO_USER:-}"
if [ -z "$REAL_USER" ]; then REAL_USER="$(logname 2>/dev/null || true)"; fi
if [ -z "$REAL_USER" ] || [ "$REAL_USER" = "root" ]; then REAL_USER="$(getent passwd 1000 | cut -d: -f1)"; fi
if [ -z "$REAL_USER" ] || [ "$REAL_USER" = "root" ]; then echo "[!] Не определён обычный пользователь. Запустите через sudo из-под своего логина."; exit 1; fi
REAL_HOME="$(getent passwd "$REAL_USER" | cut -d: -f6)"
echo "[+] Пользователь: $REAL_USER ($REAL_HOME)"

# 1. Сеть проверяем через apt (HTTP-зеркало, ca-certificates ещё не нужен)
if ! apt-get update; then echo "[!] Нет сети. Подключите USB-модем (заметка 06) и повторите."; exit 1; fi

# 2. Базовые утилиты ДО любого HTTPS
apt-get install -y ca-certificates curl wget

# 3. Компоненты репозиториев
if [ -f /etc/apt/sources.list.d/debian.sources ]; then
    sed -i 's/^Components:.*/Components: main contrib non-free non-free-firmware/' /etc/apt/sources.list.d/debian.sources
else
    grep -q 'non-free' /etc/apt/sources.list || sed -i 's/ main/ main contrib non-free non-free-firmware/' /etc/apt/sources.list
fi
apt-get update
apt-get upgrade -y

# 4. Toolchain (libcurl4-openssl-dev нужен llama.cpp)
apt-get install -y linux-headers-amd64 build-essential dkms pkg-config git cmake ninja-build libssl-dev libcurl4-openssl-dev rsync zip gdb python3 python3-venv python3-dev

# 5. /tmp в trixie = tmpfs; переводим на диск (生效 после перезагрузки)
systemctl mask tmp.mount

# 6. Репозиторий NVIDIA + драйвер (compute-only)
TEMP_DIR=/var/cache/ivc_ai_install
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"
wget -q https://developer.download.nvidia.com/compute/cuda/repos/debian13/x86_64/cuda-keyring_1.1-1_all.deb
[ -s cuda-keyring_1.1-1_all.deb ] || { echo "[!] keyring не скачан"; exit 1; }
dpkg -i cuda-keyring_1.1-1_all.deb
apt-get update
if ! apt-cache show nvidia-driver-pinning-620 >/dev/null 2>&1; then
    echo "[!] nvidia-driver-pinning-620 не найден. Доступные ветки:"; apt-cache search '^nvidia-driver-pinning' || true; exit 1
fi
apt-get install -y nvidia-driver-pinning-620
apt-get update
apt-get install -y nvidia-driver-cuda nvidia-kernel-open-dkms

# 7. CUDA Toolkit (nvcc!) из NVIDIA-репо, НЕ debian-овский nvidia-cuda-toolkit
apt-get install -y cuda-toolkit
/usr/local/cuda/bin/nvcc --version

dkms status || true
echo "=== ЭТАП А ЗАВЕРШЁН. После перезагрузки: sudo bash /var/tmp/setup_part2.sh ==="
read -r -p "Enter для перезагрузки..."
reboot
```

## Этап Б: после перезагрузки
Тома (с миграцией старого home), TRIM, zram, SSH-ключ, Docker + GPU, nvm/pnpm/uv, llama.cpp (sm_120), модель Q5_K_M (все шарды, wget -c).

```bash
#!/bin/bash
set -Eeuo pipefail
trap 'echo "[!] ОШИБКА: строка $LINENO, код $?" >&2' ERR
exec > >(tee -a /var/log/ivc_ai_setup.log) 2>&1
export DEBIAN_FRONTEND=noninteractive
cd /
echo "=== ЭТАП Б: $(date) ==="
if [ "$EUID" -ne 0 ]; then echo "[!] Запустите: sudo bash /var/tmp/setup_part2.sh"; exit 1; fi

REAL_USER="${SUDO_USER:-}"
if [ -z "$REAL_USER" ]; then REAL_USER="$(logname 2>/dev/null || true)"; fi
if [ -z "$REAL_USER" ] || [ "$REAL_USER" = "root" ]; then REAL_USER="$(getent passwd 1000 | cut -d: -f1)"; fi
if [ -z "$REAL_USER" ] || [ "$REAL_USER" = "root" ]; then echo "[!] Не определён обычный пользователь."; exit 1; fi
REAL_HOME="$(getent passwd "$REAL_USER" | cut -d: -f6)"
echo "[+] Пользователь: $REAL_USER ($REAL_HOME)"

# 1. Драйвер и nvcc
if ! nvidia-smi; then echo "[!] Драйвер не активен: Secure Boot (заметка 01)? dkms status?"; exit 1; fi
/usr/local/cuda/bin/nvcc --version

# 2. Тома lv_docker / lv_home (идемпотентно)
if mountpoint -q /home && mountpoint -q /var/lib/docker; then
    echo "[+] Тома уже смонтированы — форматирование пропущено."
else
    echo "[!] Будут отформатированы lv_docker и lv_home. Данные уничтожаются."
    read -r -p "Введите yes: " CONFIRM
    [ "$CONFIRM" = "yes" ] || { echo "Отмена."; exit 1; }
    [ -b /dev/vg0/lv_docker ] && [ -b /dev/vg0/lv_home ] || { echo "[!] LV не найдены. Проверьте разметку (заметка 02)."; exit 1; }
    if [ -d "$REAL_HOME" ] && ! mountpoint -q /home; then mv "$REAL_HOME" "${REAL_HOME}.old-on-root"; fi
    umount -l /home 2>/dev/null || true
    umount -l /var/lib/docker 2>/dev/null || true
    mkfs.ext4 -F -m 1 -L docker /dev/vg0/lv_docker
    mkfs.ext4 -F -m 1 -L home /dev/vg0/lv_home
    grep -q 'lv_docker' /etc/fstab || echo '/dev/mapper/vg0-lv_docker /var/lib/docker ext4 defaults,noatime 0 2' >> /etc/fstab
    grep -q 'lv_home' /etc/fstab || echo '/dev/mapper/vg0-lv_home /home ext4 defaults,noatime 0 2' >> /etc/fstab
    mkdir -p /var/lib/docker /home
    mount -a
    mkdir -p "$REAL_HOME"
    if [ -d "${REAL_HOME}.old-on-root" ]; then rsync -a "${REAL_HOME}.old-on-root/" "$REAL_HOME/"; echo "[+] Старый home перенесён. Резерв: ${REAL_HOME}.old-on-root (удалите вручную позже)."; fi
    chown -R "$REAL_USER:$REAL_USER" "$REAL_HOME"
fi

# 3. Артефакты Этапа А -> в home (не удаляем)
if [ -d /var/cache/ivc_ai_install ]; then
    mkdir -p "$REAL_HOME/downloads/install_backup"
    mv /var/cache/ivc_ai_install/* "$REAL_HOME/downloads/install_backup/" 2>/dev/null || true
    rmdir /var/cache/ivc_ai_install 2>/dev/null || true
    chown -R "$REAL_USER:$REAL_USER" "$REAL_HOME/downloads"
fi

# 4. Каталоги: большие данные на lv_home, /opt/ivc_ai — симлинки
sudo -u "$REAL_USER" -H bash -c 'mkdir -p ~/src ~/downloads ~/models ~/projects'
mkdir -p /opt/ivc_ai/pi /opt/ivc_ai/logs
ln -sfn "$REAL_HOME/models" /opt/ivc_ai/models
ln -sfn "$REAL_HOME/src/llama.cpp" /opt/ivc_ai/llama.cpp
chown -R "$REAL_USER:$REAL_USER" /opt/ivc_ai

# 5. TRIM + zram + sysctl
systemctl enable --now fstrim.timer
apt-get install -y systemd-zram-generator
cat > /etc/systemd/zram-generator.conf <<'EOF'
[zram0]
zram-size = min(ram / 2, 32768)
compression-algorithm = zstd
EOF
systemctl daemon-reload
systemctl start systemd-zram-setup@zram0.service
echo 'vm.swappiness=100' > /etc/sysctl.d/99-ivc-ai.conf
echo 'vm.page-cluster=0' >> /etc/sysctl.d/99-ivc-ai.conf
sysctl --system >/dev/null
swapon --show

# 6. SSH: ключ из ~/ssh_pubkey_to_add.pub, валидация ДО отключения паролей
PUB="$REAL_HOME/ssh_pubkey_to_add.pub"
if [ -s "$PUB" ] && grep -qE '^(ssh-|ecdsa-|sk-)' "$PUB"; then
    sudo -u "$REAL_USER" -H bash -c 'mkdir -p ~/.ssh'
    chmod 700 "$REAL_HOME/.ssh"
    cat "$PUB" >> "$REAL_HOME/.ssh/authorized_keys"
    chmod 600 "$REAL_HOME/.ssh/authorized_keys"
    chown -R "$REAL_USER:$REAL_USER" "$REAL_HOME/.ssh"
    sed -i -E 's/^#?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
    systemctl restart ssh
    echo "[+] Ключ добавлен, вход по паролю отключён."
else
    echo "[!] Ключ не найден/пуст ($PUB) — парольный вход НЕ отключён."
fi

# 7. Docker (ключ .asc, gnupg не нужен)
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
{
echo 'Types: deb'
echo 'URIs: https://download.docker.com/linux/debian'
echo "Suites: $VERSION_CODENAME"
echo 'Components: stable'
echo "Architectures: $(dpkg --print-architecture)"
echo 'Signed-By: /etc/apt/keyrings/docker.asc'
} > /etc/apt/sources.list.d/docker.sources
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "builder": { "gc": { "defaultKeepStorage": "20GB" } }
}
EOF
systemctl restart docker
usermod -aG docker "$REAL_USER"
docker --version

# 8. NVIDIA Container Toolkit (armored-ключ .asc, без gpg)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey -o /usr/share/keyrings/nvidia-container-toolkit.asc
echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit.asc] https://nvidia.github.io/libnvidia-container/stable/deb/$(dpkg --print-architecture) /" > /etc/apt/sources.list.d/nvidia-container-toolkit.list
apt-get update
apt-get install -y nvidia-container-toolkit
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker

# 9. Инструменты пользователя (nvm/pnpm/uv ставятся в его home)
sudo -u "$REAL_USER" -H bash -c 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.41.0/install.sh | bash'
sudo -u "$REAL_USER" -H bash -c 'export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"; nvm install --lts; nvm alias default "lts/*"'
sudo -u "$REAL_USER" -H bash -c 'curl -fsSL https://get.pnpm.io | sh -'
sudo -u "$REAL_USER" -H bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'

# 10. llama.cpp: nvcc из /usr/local/cuda, arch 120 (Blackwell)
sudo -u "$REAL_USER" -H bash -c 'export PATH=/usr/local/cuda/bin:$PATH; cd ~/src; if [ ! -d llama.cpp ]; then git clone --depth 1 https://github.com/ggml-org/llama.cpp; fi; cd llama.cpp; cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=120 -DCMAKE_BUILD_TYPE=Release; cmake --build build --config Release --target llama-cli llama-server llama-bench -j"$(nproc)"'
sudo -u "$REAL_USER" -H bash -c '~/src/llama.cpp/build/bin/llama-cli --version'

# 11. Модель: список файлов через HF API (возможны шарды), wget с докачкой
read -r -p "Скачать модель Q5_K_M (~24 ГБ) с Hugging Face? yes/no: " DL_MODEL
if [ "$DL_MODEL" = "yes" ]; then
    AVAIL_KB=$(df -Pk "$REAL_HOME" | awk 'NR==2 {print $4}')
    if [ "$AVAIL_KB" -lt 31457280 ]; then echo "[!] Мало места (<30 ГБ) на /home"; exit 1; fi
    HF_TOKEN="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"
    REPO="IsValorum/Cyber-Tiel-Coder-35B-A3B-APEX-I-MiniPlus-V2.1-GGUF"
    curl -fsSL -H "Authorization: Bearer $HF_TOKEN" "https://huggingface.co/api/models/$REPO/tree/main?recursive=true" -o /var/tmp/hf_tree.json
    python3 -c 'import json;[print(x["path"]) for x in json.load(open("/var/tmp/hf_tree.json")) if x["path"].endswith(".gguf") and "Q5_K_M" in x["path"]]' > /var/tmp/hf_files.txt
    if [ ! -s /var/tmp/hf_files.txt ]; then echo "[!] Файлы Q5_K_M не найдены в репозитории"; exit 1; fi
    cat /var/tmp/hf_files.txt
    while IFS= read -r f; do
        sudo -u "$REAL_USER" -H wget -c --tries=3 --timeout=30 --header="Authorization: Bearer $HF_TOKEN" -P "$REAL_HOME/models" "https://huggingface.co/$REPO/resolve/main/$f"
    done < /var/tmp/hf_files.txt
    ls -lh "$REAL_HOME/models"
fi

echo "=== ЭТАП Б ЗАВЕРШЁН ==="
echo "Перелогиньтесь (или newgrp docker) для группы docker и PATH nvm/pnpm/uv."
```

## Что проверяется автоматически
- Сеть и зеркала (apt update), наличие keyring-файла, наличие pinning-пакета
- nvcc --version, nvidia-smi, dkms status
- Существование LV, смонтированность томов (повторный запуск безопасен)
- Формат SSH-ключа до отключения парольного входа
- Свободное место (>30 ГБ) перед скачиванием модели
- llama-cli --version, swapon --show, docker --version

## Связи
- [[01_BIOS_Preparation]]
- [[02_Debian_Installation]]
- [[04_NVIDIA_Drivers]]
- [[05_AI_Tools_Setup]]
- [[06_Network_Fix_USB_Modem]]
- [[08_Hardware_Profile]]
