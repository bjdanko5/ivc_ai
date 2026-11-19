---
created: 2026-11-19
tags:
  - automation
  - bash
  - nvidia
  - docker
---

# Скрипты автоматизации настройки сервера

## Этап А: До первой перезагрузки
Запускается сразу после установки системы. Устанавливает драйвер NVIDIA (ветка 620) и обновляет репозитории.

```bash
#!/bin/bash
set -e

echo "=== ЭТАП А: Базовая настройка и драйвер NVIDIA ==="
read -p "Убедитесь, что интернет работает (USB-модем). Нажмите Enter..."

# 1. Создание структуры каталогов
mkdir -p ~/src ~/downloads ~/models ~/projects

# 2. Обновление репозиториев
echo "[+] Обновление sources.list..."
if [ -f /etc/apt/sources.list.d/debian.sources ]; then
    sudo sed -i 's/^Components:\(.*\)$/Components:\1 contrib non-free/' /etc/apt/sources.list.d/debian.sources
else
    sudo sed -i 's/main/main contrib non-free non-free-firmware/g' /etc/apt/sources.list
fi

sudo apt update
sudo apt full-upgrade -y

# 3. Установка инструментов сборки
echo "[+] Установка build-essential и headers..."
sudo apt install -y linux-headers-amd64 build-essential dkms pkg-config git cmake libssl-dev rsync zip gdb ninja-build python3-venv python3-dev

# 4. Отключение tmpfs для /tmp
echo "[+] Маскировка tmp.mount..."
sudo systemctl mask tmp.mount

# 5. Установка драйвера NVIDIA
echo "[+] Установка CUDA Keyring и драйвера ветки 620..."
cd ~/downloads
wget https://developer.download.nvidia.com/compute/cuda/repos/debian13/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
rm cuda-keyring_1.1-1_all.deb

sudo apt update
sudo apt install -y nvidia-driver-pinning-620
sudo apt update
sudo apt -V install -y nvidia-driver-cuda nvidia-kernel-open-dkms

echo "=== ЭТАП А ЗАВЕРШЕН ==="
read -p "Нажмите Enter для перезагрузки системы..."
sudo reboot
```

## Этап Б: После перезагрузки
Форматирует LVM-тома, настраивает Docker, zram, Node.js, pnpm, uv и собирает llama.cpp.

**Внимание:** Этот скрипт удаляет данные на томах Docker и Home!

```bash
#!/bin/bash
set -e

echo "=== ЭТАП Б: Диски, Docker, Языки и AI ==="
read -p "Система перезагружена. Нажмите Enter для продолжения..."

# 1. Проверка драйвера NVIDIA
nvidia-smi || echo "ВНИМАНИЕ: nvidia-smi не сработала."

# 2. Форматирование LVM томов
echo "[!] ВНИМАНИЕ: Следующий шаг отформатирует lv_docker и lv_home!"
read -p "Введите 'yes' для подтверждения форматирования: " CONFIRM
if [ "$CONFIRM" == "yes" ]; then
    sudo systemctl isolate rescue.target
    sleep 5
    sudo umount /home 2>/dev/null || true
    sudo umount /var/lib/docker 2>/dev/null || true
    sudo mkfs.ext4 -T news -m 1 -L docker /dev/vg0/lv_docker
    sudo mkfs.ext4 -T news -m 1 -L home /dev/vg0/lv_home
    grep -q "lv_docker" /etc/fstab || echo "/dev/mapper/vg0-lv_docker  /var/lib/docker  ext4  defaults,noatime  0  2" | sudo tee -a /etc/fstab
    grep -q "lv_home" /etc/fstab || echo "/dev/mapper/vg0-lv_home    /home            ext4  defaults,noatime  0  2" | sudo tee -a /etc/fstab
    sudo mkdir -p /var/lib/docker /home
    sudo mount -a
    sudo chown $USER:$USER /home/$USER
    sudo systemctl default
    sleep 5
    echo "[+] Тома отформатированы и смонтированы."
else
    echo "Форматирование пропущено."
fi

# 3. zram
sudo apt install -y systemd-zram-generator
cat <<EOF | sudo tee /etc/systemd/zram-generator.conf
[zram0]
zram-size = min(ram / 2, 32768)
compression-algorithm = zstd
EOF
sudo systemctl daemon-reload
sudo systemctl start /dev/zram0

# 4. Docker
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "Types: deb" | sudo tee /etc/apt/sources.list.d/docker.sources
echo "URIs: https://download.docker.com/linux/debian" | sudo tee -a /etc/apt/sources.list.d/docker.sources
echo "Suites: $(. /etc/os-release && echo \$VERSION_CODENAME)" | sudo tee -a /etc/apt/sources.list.d/docker.sources
echo "Components: stable" | sudo tee -a /etc/apt/sources.list.d/docker.sources
echo "Architectures: $(dpkg --print-architecture)" | sudo tee -a /etc/apt/sources.list.d/docker.sources
echo "Signed-By: /etc/apt/keyrings/docker.asc" | sudo tee -a /etc/apt/sources.list.d/docker.sources
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Настройка логов Docker
sudo mkdir -p /etc/docker
cat <<EOF | sudo tee /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "builder": { "gc": { "defaultKeepStorage": "20GB" } }
}
EOF
sudo systemctl restart docker
sudo usermod -aG docker $USER

# 5. NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 6. Языки программирования
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.41.0/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install --lts
curl -fsSL https://get.pnpm.io | sh -
curl -LsSf https://astral.sh/uv/install.sh | sh

# 7. Сборка llama.cpp
cd ~/src
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="120" -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release --target llama-cli llama-server llama-bench -j$(nproc)

echo "=== НАСТРОЙКА ЗАВЕРШЕНА ==="
```

## Ключевые компоненты
- **NVIDIA Driver:** Compute-only, ветка 620+ для RTX 5070 Ti.
- **Docker:** Настроен с ограничением логов и поддержкой GPU.
- **Языки:** Node.js (LTS через nvm), pnpm, uv.
- **AI:** llama.cpp со сборкой под CUDA arch 120 (Blackwell).

## Связи
- [[Debian_Server_Setup]]
- [[04_NVIDIA_Drivers]]
- [[05_AI_Tools_Setup]]
- [[06_Network_Fix_USB_Modem]]
