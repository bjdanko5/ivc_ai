---
created: 2026-11-19
updated: 2026-11-19
tags:
  - server-setup
---

# 10. Walkthrough: ручной режим

Каждый шаг - отдельный блок: команда, проверка, если не так. Автоматический эквивалент - [[07_Automation_Scripts]] (источник правды). Порядок блоков совпадает с этапами 07.
Все команды на сервере, если не указано иное. sudo presupposes пустой root-пароль при установке (02).

## 0. Клиент (Windows)
```bat
ssh-keygen -t ed25519 -f C:\Temp\ivc_deploy\id_ed25519 -N "" -C "ivc_ai deploy"
scp C:\Temp\ivc_deploy\setup_part1.sh C:\Temp\ivc_deploy\setup_part2.sh user@IP:/var/tmp/
scp C:\Temp\ivc_deploy\id_ed25519.pub user@IP:ssh_pubkey_to_add.pub
```
Проверка: ssh user@IP по паролю заходит. Если не так - [[09_Client_File_Delivery]], [[06_Network_Fix_USB_Modem]].

## 1-2. BIOS и установщик
Чеклисты без команд: [[01_BIOS_Preparation]], [[02_Debian_Installation]]. Критично: Secure Boot off, CSM off, root-пароль пуст, только SSH server + standard, lv_docker/lv_home = do not use.

## 3. Первая загрузка и сеть
```bash
ip -br link
ip -br addr
```
Нет адреса на встроенной NIC: модем по 06, либо сразу блок 6A ниже (firmware-realtek).

## 4A. База + SSH + KillMode (Этап А, шаги 1-3)
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl wget openssh-server firmware-realtek
sudo systemctl enable --now ssh
sudo mkdir -p /etc/systemd/system/ssh.service.d
printf '%s\n' '[Service]' 'KillMode=process' | sudo tee /etc/systemd/system/ssh.service.d/killmode.conf
sudo systemctl daemon-reload
```
Проверка: systemctl is-active ssh = active. Если apt update падает - сеть, 06.

## 4B. Ранний ключ (Этап А, шаг 4)
```bash
install -d -m 700 -o "$USER" -g "$USER" ~/.ssh
touch ~/.ssh/authorized_keys
grep -qxF "$(cat ~/ssh_pubkey_to_add.pub)" ~/.ssh/authorized_keys || cat ~/ssh_pubkey_to_add.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
sudo systemctl reload ssh
```
Проверка с клиента: ssh -i C:\Temp\ivc_deploy\id_ed25519 user@IP - вход без пароля. Пароли пока НЕ отключать.

## 4C. Репозитории и upgrade (Этап А, шаг 5)
```bash
sudo sed -i 's/^Components:.*/Components: main contrib non-free non-free-firmware/' /etc/apt/sources.list.d/debian.sources
sudo apt-get update
sudo apt-get upgrade -y
```
Проверка: apt-cache policy | grep non-free. Сессия не должна оборваться (KillMode уже стоит).

## 4D. Диагностика NIC (Этап А, шаг 6)
```bash
ip -br link
lspci -nnk | grep -A3 -i ethernet
```
Realtek без линка после firmware-realtek: backports-ядро из 06, затем перезагрузка и возврат к 4E.

## 4E. Toolchain и /tmp (Этап А, шаги 7-8)
```bash
sudo apt-get install -y linux-headers-amd64 build-essential dkms pkg-config git cmake ninja-build libssl-dev libcurl4-openssl-dev rsync zip gdb python3 python3-venv python3-dev
sudo systemctl mask tmp.mount
```
Проверка: cmake --version, gcc --version. /tmp станет диском после перезагрузки.

## 4F. Драйвер NVIDIA (Этап А, шаг 9)
```bash
sudo mkdir -p /var/cache/ivc_ai_install && cd /var/cache/ivc_ai_install
sudo wget -q https://developer.download.nvidia.com/compute/cuda/repos/debian13/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
apt-cache show nvidia-driver-pinning-620 >/dev/null 2>&1 || apt-cache search '^nvidia-driver-pinning'
sudo apt-get install -y nvidia-driver-pinning-620
sudo apt-get update
sudo apt-get install -y nvidia-driver-cuda nvidia-kernel-open-dkms
```
Проверка: dkms status показывает nvidia/... installed. Если pinning-620 нет - выбрать ветку из вывода search и подставить её номер.

## 4G. CUDA и перезагрузка (Этап А, шаг 10)
```bash
sudo apt-get install -y cuda-toolkit
/usr/local/cuda/bin/nvcc --version
dkms status
sync
sudo reboot
```
Если не так: nvcc нет - пакет cuda-toolkit не встал (смотреть apt-вывод); после reboot nvidia-smi молчит - Secure Boot (01) или dkms.

## 5A. Проверки после перезагрузки (Этап Б, шаг 1)
```bash
nvidia-smi
/usr/local/cuda/bin/nvcc --version
```

## 5B. Тома и миграция home (Этап Б, шаг 2) - ОСТОРОЖНО
```bash
findmnt /home /var/lib/docker
sudo mv "$HOME" /var/tmp/ivc_home_old
sudo umount -l /home 2>/dev/null || true
sudo umount -l /var/lib/docker 2>/dev/null || true
sudo mkfs.ext4 -F -m 1 -L docker /dev/vg0/lv_docker
sudo mkfs.ext4 -F -m 1 -L home /dev/vg0/lv_home
echo '/dev/mapper/vg0-lv_docker /var/lib/docker ext4 defaults,noatime 0 2' | sudo tee -a /etc/fstab
echo '/dev/mapper/vg0-lv_home /home ext4 defaults,noatime 0 2' | sudo tee -a /etc/fstab
sudo mkdir -p /var/lib/docker /home
sudo mount -a
sudo mkdir -p "$HOME"
sudo rsync -a /var/tmp/ivc_home_old/ "$HOME/"
sudo chown -R "$USER:$USER" "$HOME"
```
Проверка: findmnt показывает оба тома; ls ~ видит .ssh и ssh_pubkey_to_add.pub; df -h /home ~400G.
Если не так: /var/tmp/ivc_home_old уже существует - прошлый прогон, разобрать вручную; LV нет - разметка 02; строки fstab дублируются - удалить лишние вручную.
Бэкап /var/tmp/ivc_home_old удалить только после полной проверки.

## 5C. SSH hardening (Этап Б, шаг 3)
Сначала в НОВОМ окне клиента: ssh -i ... user@IP без пароля. Затем:
```bash
sudo cp -a /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.manual
sudo mkdir -p /etc/ssh/sshd_config.d
printf '%s\n' 'PasswordAuthentication no' 'KbdInteractiveAuthentication no' 'PubkeyAuthentication yes' | sudo tee /etc/ssh/sshd_config.d/99-ivc-hardening.conf
sudo sed -i -E 's/^#?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sshd -t
sudo systemctl reload ssh
```
Проверка: новое окно ssh по ключу заходит; по паролю - отказ. Если sshd -t ругается - вернуть бэкап и исправить drop-in. Текущая сессия не рвётся (reload + KillMode).

## 5D. Артефакты и каталоги (Этап Б, шаги 4-5)
```bash
mkdir -p ~/downloads/install_backup
sudo mv /var/cache/ivc_ai_install/* ~/downloads/install_backup/ 2>/dev/null || true
sudo rmdir /var/cache/ivc_ai_install 2>/dev/null || true
mkdir -p ~/src ~/downloads ~/models ~/projects
sudo mkdir -p /opt/ivc_ai/pi /opt/ivc_ai/logs
sudo ln -sfn "$HOME/models" /opt/ivc_ai/models
sudo ln -sfn "$HOME/src/llama.cpp" /opt/ivc_ai/llama.cpp
sudo chown -R "$USER:$USER" /opt/ivc_ai "$HOME/downloads"
```

## 5E. TRIM, zram, sysctl (Этап Б, шаг 6)
```bash
sudo systemctl enable --now fstrim.timer
sudo apt-get install -y systemd-zram-generator
printf '%s\n' '[zram0]' 'zram-size = min(ram / 2, 32768)' 'compression-algorithm = zstd' | sudo tee /etc/systemd/zram-generator.conf
sudo systemctl daemon-reload
sudo systemctl start systemd-zram-setup@zram0.service
printf '%s\n' 'vm.swappiness=100' 'vm.page-cluster=0' | sudo tee /etc/sysctl.d/99-ivc-ai.conf
sudo sysctl --system
swapon --show
```
Проверка: swapon показывает zram0 (приоритет выше) и lv_swap. Если zram нет - journalctl -u systemd-zram-setup@zram0.

## 5F. Docker (Этап Б, шаг 7)
```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
printf '%s\n' 'Types: deb' 'URIs: https://download.docker.com/linux/debian' "Suites: $VERSION_CODENAME" 'Components: stable' "Architectures: $(dpkg --print-architecture)" 'Signed-By: /etc/apt/keyrings/docker.asc' | sudo tee /etc/apt/sources.list.d/docker.sources
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
printf '%s\n' '{' '  "log-driver": "json-file",' '  "log-opts": { "max-size": "10m", "max-file": "3" },' '  "builder": { "gc": { "defaultKeepStorage": "20GB" } }' '}' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker
sudo usermod -aG docker "$USER"
docker --version
```
Проверка: docker info без sudo - только после перелогина (newgrp docker). Если apt update ругается на ключ - файл docker.asc пуст/битый, перекачать.

## 5G. NVIDIA Container Toolkit (Этап Б, шаг 8)
```bash
sudo curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey -o /usr/share/keyrings/nvidia-container-toolkit.asc
echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit.asc] https://nvidia.github.io/libnvidia-container/stable/deb/$(dpkg --print-architecture) /" | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```
Опциональная проверка GPU в контейнере (тянет образ ubuntu): docker run --rm --gpus all ubuntu nvidia-smi.

## 5H. Языки пользователя (Этап Б, шаг 9)
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.41.0/install.sh | bash
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"; nvm install --lts; nvm alias default 'lts/*'
curl -fsSL https://get.pnpm.io | sh -
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Выполнять ОТ ОБЫЧНОГО пользователя (не sudo). Проверка после перелогина: node -v, pnpm -v, uv --version.

## 5I. llama.cpp (Этап Б, шаг 10)
```bash
export PATH=/usr/local/cuda/bin:$PATH
cd ~/src
git clone --depth 1 https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=120 -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release --target llama-cli llama-server llama-bench -j"$(nproc)"
./build/bin/llama-cli --version
```
Если cmake не находит nvcc - PATH не экспортирован; если CURL not found - не стоит libcurl4-openssl-dev (4E).

## 5J. Модель (Этап Б, шаг 11)
Явные имена файлов (ручной режим):
```bash
export HF_TOKEN="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"
cd ~/models
wget -c --header="Authorization: Bearer $HF_TOKEN" https://huggingface.co/IsValorum/Cyber-Tiel-Coder-35B-A3B-APEX-I-NanoPlus-GGUF/resolve/main/Cyber-Tiel-Coder-35B-A3B.APEX-I-NanoPlus.gguf
wget -c --header="Authorization: Bearer $HF_TOKEN" https://huggingface.co/IsValorum/Cyber-Tiel-Coder-35B-A3B-APEX-I-NanoPlus-GGUF/resolve/main/mmproj-Q8_0.gguf
wget -c --header="Authorization: Bearer $HF_TOKEN" https://huggingface.co/IsValorum/Cyber-Tiel-Coder-35B-A3B-APEX-I-NanoPlus-GGUF/resolve/main/mtp-Cyber-Tiel-Coder-35B-A3B.gguf
wget -c --header="Authorization: Bearer $HF_TOKEN" https://huggingface.co/IsValorum/Cyber-Tiel-Coder-35B-A3B-APEX-I-NanoPlus-GGUF/resolve/main/chat_template.jinja
ls -lh
```
Проверка: основной файл ~12.5 ГБ (не LFS-заглушка). Если 404 - имена в репозитории отличаются: список через API как в 07 (curl tree/main + фильтр).

## 5K. Launcher и юнит (Этап Б, шаг 12)
Создать /opt/ivc_ai/run-llama-server.sh и /etc/systemd/system/llama-server.service содержимым из 07 (блоки heredoc), затем:
```bash
sudo chmod 755 /opt/ivc_ai/run-llama-server.sh
sudo systemctl daemon-reload
sudo systemctl enable --now llama-server
curl -sf http://127.0.0.1:8080/health && echo OK
journalctl -u llama-server -n 50 --no-pager
```
Проверка: в journal строка [launcher] ctx=... kv=... - выбранная конфигурация; health OK. Если все конфигурации упали - смотреть VRAM: nvidia-smi во время загрузки.
Клиент: ssh -L 8080:127.0.0.1:8080 user@IP, затем http://127.0.0.1:8080.

## 6. Откаты и частые отказы
| Симптом | Действие |
|---|---|
| bash: \r: command not found | sed -i 's/\r$//' /var/tmp/setup_part*.sh (09) |
| ssh перестал пускать по паролю, ключ не работает | консоль: sudo rm /etc/ssh/sshd_config.d/99-ivc-hardening.conf; sudo cp /etc/ssh/sshd_config.bak.manual /etc/ssh/sshd_config; sudo systemctl reload ssh |
| nvidia-smi пусто после reboot | Secure Boot (01); dkms status; journalctl -k | grep -i nvidia |
| llama-server OOM на всех ctx | уменьшить стартовый ctx в launcher до 32768; проверить nvidia-smi |
| /home пуст после 5B | данные в /var/tmp/ivc_home_old, rsync повторить |
| сеть пропала после снятия телефона | 06: firmware-realtek / backports-ядро |

## Связи
- [[07_Automation_Scripts]]
- [[01_BIOS_Preparation]]
- [[02_Debian_Installation]]
- [[06_Network_Fix_USB_Modem]]
- [[09_Client_File_Delivery]]

