---
created: 2026-11-19
updated: 2026-11-19
tags:
  - automation
  - bash
  - nvidia
  - docker
  - ssh
---

# Скрипты автоматизации настройки сервера

## Порядок работы (флоу)
1. BIOS ([[01_BIOS_Preparation]]), Debian с галкой SSH server ([[02_Debian_Installation]]).
2. Нет сети - USB-модем с консоли ([[06_Network_Fix_USB_Modem]]).
3. Доставка скриптов и публичного ключа с клиента: [[09_Client_File_Delivery]] (scp/WinSCP, `C:\Temp\ivc_deploy`).
4. Этап А: `sudo bash /var/tmp/setup_part1.sh` - firmware-realtek, openssh, KillMode=process, ключ, драйвер, CUDA. Перезагрузка.
5. С клиента: `ssh ivc-ai` по ключу.
6. Этап Б: `sudo bash /var/tmp/setup_part2.sh` - диски+миграция, hardening SSH, Docker, языки, llama.cpp, NanoPlus, юнит llama-server.

Лог: `/var/log/ivc_ai_setup.log`. Ошибка = стоп с номером строки. Повторный запуск безопасен. Бэкап home: `/var/tmp/ivc_home_old`.

## Сеть: Realtek RTL8125D (контингентность)
Этап А ставит firmware-realtek. Ревизия 0x689 может не поддерживаться ядром 6.12 - тогда USB-модем лишь костыль. Запасной путь (DKMS пересоберёт драйвер сам):
```bash
echo 'deb http://deb.debian.org/debian trixie-backports main contrib non-free non-free-firmware' > /etc/apt/sources.list.d/backports.list
apt-get update
apt-get -t trixie-backports install -y linux-image-amd64 linux-headers-amd64
reboot
```

## Модель: NanoPlus и математика VRAM
Репозиторий: IsValorum/Cyber-Tiel-Coder-35B-A3B-APEX-I-NanoPlus-GGUF. Основной gguf ~12.55 ГБ - помещается в 16 ГБ VRAM целиком, `-ngl 99`, без CPU-offload. Дополнительно: mmproj-Q8_0.gguf (vision), mtp-...gguf (draft, `--spec-type draft-mtp`), chat_template.jinja (`--chat-template-file`, reasoning_effort medium).
Sampling для кода: repeat/presence/frequency penalty = 0/1.0 (иначе модель начинает подменять `{` на `=` и ломать отступы), temp 0.6, top_p 0.95, top_k 20, min_p 0 (альтернатива из advisory: 0.05).
ctx 262144 - зона риска по KV: launcher пробует 262144/f16, 262144/q8_0 KV, 131072/q8_0, 65536/q8_0 и логирует выбранную. Флаги --reasoning-effort/--spec-type проверяются по --help; при отсутствии - fallback без падения.
Таблица VRAM в [[08_Hardware_Profile]] относится к MiniPlus-квантам и для них занижена; для NanoPlus вывод 'влезает' верен.

## Этап А: до первой перезагрузки

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
if [ -z "$REAL_USER" ] || [ "$REAL_USER" = "root" ]; then echo "[!] Не определён обычный пользователь."; exit 1; fi
REAL_HOME="$(getent passwd "$REAL_USER" | cut -d: -f6)"
echo "[+] Пользователь: $REAL_USER ($REAL_HOME)"

# 1. Сеть через apt (HTTP, ca-certificates ещё не нужен)
if ! apt-get update; then echo "[!] Нет сети. USB-модем (заметка 06), затем повторите."; exit 1; fi

# 2. База + SSH-сервер + firmware Realtek ДО любого HTTPS/upgrade
apt-get install -y ca-certificates curl wget openssh-server firmware-realtek
systemctl enable --now ssh

# 3. KillMode=process СРАЗУ: upgrade openssh не убьёт вашу сессию
mkdir -p /etc/systemd/system/ssh.service.d
printf '%s\n' '[Service]' 'KillMode=process' > /etc/systemd/system/ssh.service.d/killmode.conf
systemctl daemon-reload

# 4. Ранний SSH-ключ: добавляем, пароли НЕ трогаем
PUB="$REAL_HOME/ssh_pubkey_to_add.pub"
if [ -s "$PUB" ] && grep -qE '^(ssh-|ecdsa-|sk-)' "$PUB"; then
    install -d -m 700 -o "$REAL_USER" -g "$REAL_USER" "$REAL_HOME/.ssh"
    touch "$REAL_HOME/.ssh/authorized_keys"
    while IFS= read -r line; do
        grep -qxF "$line" "$REAL_HOME/.ssh/authorized_keys" || echo "$line" >> "$REAL_HOME/.ssh/authorized_keys"
    done < "$PUB"
    chmod 600 "$REAL_HOME/.ssh/authorized_keys"
    chown "$REAL_USER:$REAL_USER" "$REAL_HOME/.ssh/authorized_keys"
    systemctl reload ssh
    echo "[+] Ключ добавлен. Пароли пока включены. Проверьте с клиента: ssh $REAL_USER@<IP>"
else
    echo "[!] Ключ не найден ($PUB). Доставка: заметка 09. Продолжаем на консоли."
fi

# 5. Компоненты репозиториев
if [ -f /etc/apt/sources.list.d/debian.sources ]; then
    sed -i 's/^Components:.*/Components: main contrib non-free non-free-firmware/' /etc/apt/sources.list.d/debian.sources
else
    grep -q 'non-free' /etc/apt/sources.list || sed -i 's/ main/ main contrib non-free non-free-firmware/' /etc/apt/sources.list
fi
apt-get update
apt-get upgrade -y

# 6. Диагностика встроенной NIC
ip -br link || true
lspci -nnk | grep -A3 -i ethernet || true
echo "[i] Realtek без линка? См. раздел 'Сеть: Realtek' ниже (backports-ядро)."

# 7. Toolchain
apt-get install -y linux-headers-amd64 build-essential dkms pkg-config git cmake ninja-build libssl-dev libcurl4-openssl-dev rsync zip gdb python3 python3-venv python3-dev

# 8. /tmp tmpfs -> диск (после перезагрузки)
systemctl mask tmp.mount

# 9. NVIDIA repo + драйвер compute-only
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

# 10. CUDA Toolkit (nvcc)
apt-get install -y cuda-toolkit
/usr/local/cuda/bin/nvcc --version

dkms status || true
echo "=== ЭТАП А ЗАВЕРШЁН ==="
echo "После перезагрузки: ssh по ключу, затем sudo bash /var/tmp/setup_part2.sh"
sync
read -r -p "Enter для перезагрузки..."
reboot
```

## Этап Б: после перезагрузки

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
if ! nvidia-smi; then echo "[!] Драйвер не активен: Secure Boot (01)? dkms status?"; exit 1; fi
/usr/local/cuda/bin/nvcc --version

# 2. Тома + миграция home ВНЕ /home
if mountpoint -q /home && mountpoint -q /var/lib/docker; then
    echo "[+] Тома уже смонтированы - пропуск."
else
    echo "[!] Будут отформатированы lv_docker и lv_home."
    read -r -p "Введите yes: " CONFIRM
    [ "$CONFIRM" = "yes" ] || { echo "Отмена."; exit 1; }
    [ -b /dev/vg0/lv_docker ] && [ -b /dev/vg0/lv_home ] || { echo "[!] LV не найдены (02)."; exit 1; }
    if [ -d "$REAL_HOME" ] && ! mountpoint -q /home; then
        [ -e /var/tmp/ivc_home_old ] && { echo "[!] /var/tmp/ivc_home_old уже есть. Разберите вручную."; exit 1; }
        mv "$REAL_HOME" /var/tmp/ivc_home_old
    fi
    umount -l /home 2>/dev/null || true
    umount -l /var/lib/docker 2>/dev/null || true
    mkfs.ext4 -F -m 1 -L docker /dev/vg0/lv_docker
    mkfs.ext4 -F -m 1 -L home /dev/vg0/lv_home
    grep -q 'lv_docker' /etc/fstab || echo '/dev/mapper/vg0-lv_docker /var/lib/docker ext4 defaults,noatime 0 2' >> /etc/fstab
    grep -q 'lv_home' /etc/fstab || echo '/dev/mapper/vg0-lv_home /home ext4 defaults,noatime 0 2' >> /etc/fstab
    mkdir -p /var/lib/docker /home
    mount -a
    mkdir -p "$REAL_HOME"
    if [ -d /var/tmp/ivc_home_old ]; then rsync -a /var/tmp/ivc_home_old/ "$REAL_HOME/"; echo "[+] home перенесён. Бэкап: /var/tmp/ivc_home_old"; fi
    chown -R "$REAL_USER:$REAL_USER" "$REAL_HOME"
fi

# 3. SSH hardening после миграции
AK="$REAL_HOME/.ssh/authorized_keys"
if [ -s "$AK" ] && grep -qE '^(ssh-|ecdsa-|sk-)' "$AK"; then
    echo "[+] ОТКРОЙТЕ НОВОЕ окно на клиенте: ssh $REAL_USER@<IP> (по ключу)"
    read -r -p "Вход по ключу прошёл без пароля? yes/no: " SSH_OK
    if [ "$SSH_OK" = "yes" ]; then
        cp -a /etc/ssh/sshd_config "/etc/ssh/sshd_config.bak.$(date +%Y%m%d%H%M%S)"
        mkdir -p /etc/ssh/sshd_config.d
        printf '%s\n' 'PasswordAuthentication no' 'KbdInteractiveAuthentication no' 'PubkeyAuthentication yes' > /etc/ssh/sshd_config.d/99-ivc-hardening.conf
        sed -i -E 's/^#?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
        mkdir -p /etc/systemd/system/ssh.service.d
        printf '%s\n' '[Service]' 'KillMode=process' > /etc/systemd/system/ssh.service.d/killmode.conf
        systemctl daemon-reload
        sshd -t
        systemctl reload ssh
        python3 -c 'import socket; s=socket.create_connection(("127.0.0.1",22),5); print("[+] sshd отвечает:", s.recv(64).decode().strip()); s.close()'
        echo "[+] Пароли отключены, сессия сохранена."
    else
        echo "[!] Hardening пропущен."
    fi
else
    echo "[!] authorized_keys пуст (доставка: заметка 09). Пароли сохранены."
fi

# 4. Артефакты Этапа А -> home
if [ -d /var/cache/ivc_ai_install ]; then
    mkdir -p "$REAL_HOME/downloads/install_backup"
    mv /var/cache/ivc_ai_install/* "$REAL_HOME/downloads/install_backup/" 2>/dev/null || true
    rmdir /var/cache/ivc_ai_install 2>/dev/null || true
    chown -R "$REAL_USER:$REAL_USER" "$REAL_HOME/downloads"
fi

# 5. Каталоги
sudo -u "$REAL_USER" -H bash -c 'mkdir -p ~/src ~/downloads ~/models ~/projects'
mkdir -p /opt/ivc_ai/pi /opt/ivc_ai/logs
ln -sfn "$REAL_HOME/models" /opt/ivc_ai/models
ln -sfn "$REAL_HOME/src/llama.cpp" /opt/ivc_ai/llama.cpp
chown -R "$REAL_USER:$REAL_USER" /opt/ivc_ai

# 6. TRIM + zram + sysctl
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

# 7. Docker
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

# 8. NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey -o /usr/share/keyrings/nvidia-container-toolkit.asc
echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit.asc] https://nvidia.github.io/libnvidia-container/stable/deb/$(dpkg --print-architecture) /" > /etc/apt/sources.list.d/nvidia-container-toolkit.list
apt-get update
apt-get install -y nvidia-container-toolkit
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker

# 9. Инструменты пользователя
sudo -u "$REAL_USER" -H bash -c 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.41.0/install.sh | bash'
sudo -u "$REAL_USER" -H bash -c 'export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"; nvm install --lts; nvm alias default "lts/*"'
sudo -u "$REAL_USER" -H bash -c 'curl -fsSL https://get.pnpm.io | sh -'
sudo -u "$REAL_USER" -H bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'

# 10. llama.cpp (sm_120)
sudo -u "$REAL_USER" -H bash -c 'export PATH=/usr/local/cuda/bin:$PATH; cd ~/src; if [ ! -d llama.cpp ]; then git clone --depth 1 https://github.com/ggml-org/llama.cpp; fi; cd llama.cpp; cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=120 -DCMAKE_BUILD_TYPE=Release; cmake --build build --config Release --target llama-cli llama-server llama-bench -j"$(nproc)"'
sudo -u "$REAL_USER" -H bash -c '~/src/llama.cpp/build/bin/llama-cli --version'

# 11. Модель NanoPlus: main + mmproj + mtp + chat_template.jinja
read -r -p "Скачать NanoPlus (~12.5 ГБ + mmproj + mtp) с Hugging Face? yes/no: " DL_MODEL
if [ "$DL_MODEL" = "yes" ]; then
    AVAIL_KB=$(df -Pk "$REAL_HOME" | awk 'NR==2 {print $4}')
    if [ "$AVAIL_KB" -lt 20971520 ]; then echo "[!] Мало места (<20 ГБ) на /home"; exit 1; fi
    HF_TOKEN="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"
    REPO="IsValorum/Cyber-Tiel-Coder-35B-A3B-APEX-I-NanoPlus-GGUF"
    curl -fsSL -H "Authorization: Bearer $HF_TOKEN" "https://huggingface.co/api/models/$REPO/tree/main?recursive=true" -o /var/tmp/hf_tree.json
    python3 -c 'import json,os;ps=[x["path"] for x in json.load(open("/var/tmp/hf_tree.json")) if x["type"]=="file"];w=[p for p in ps if p.endswith(".gguf") and not os.path.basename(p).startswith(("mmproj","mtp"))]+[p for p in ps if p.endswith(".gguf") and os.path.basename(p).startswith(("mmproj","mtp"))]+[p for p in ps if p=="chat_template.jinja"];print("\n".join(w))' > /var/tmp/hf_files.txt
    if [ "$(grep -c . /var/tmp/hf_files.txt)" -lt 3 ]; then echo "[!] В репозитории не найдены main/mmproj/mtp"; exit 1; fi
    cat /var/tmp/hf_files.txt
    while IFS= read -r f; do
        sudo -u "$REAL_USER" -H wget -c --tries=3 --timeout=30 --header="Authorization: Bearer $HF_TOKEN" -P "$REAL_HOME/models" "https://huggingface.co/$REPO/resolve/main/$f"
    done < /var/tmp/hf_files.txt
    MAIN_F="$(ls -1 "$REAL_HOME/models"/*.gguf | grep -v -E '/(mmproj|mtp)' | head -n1)"
    SZ=$(stat -c %s "$MAIN_F")
    if [ "$SZ" -lt 10000000000 ]; then echo "[!] Основной gguf подозрительно мал ($SZ байт)"; exit 1; fi
    ls -lh "$REAL_HOME/models"
fi

# 12. Launcher: полный offload (12.55 ГБ < 16 ГБ), MTP-draft, code-safe sampling,
#     ctx-fallback цепочка, автоопределение флагов по --help
cat > /opt/ivc_ai/run-llama-server.sh <<'SH'
#!/bin/bash
set -uo pipefail
D=/opt/ivc_ai/models
BIN=/opt/ivc_ai/llama.cpp/build/bin/llama-server
MAIN="$(ls -1 "$D"/*.gguf 2>/dev/null | grep -v -E '/(mmproj|mtp)' | sort | head -n1)"
[ -n "$MAIN" ] || { echo "no main gguf in $D"; exit 1; }
MM="$(ls -1 "$D"/mmproj*.gguf 2>/dev/null | head -n1)"
MTP="$(ls -1 "$D"/mtp*.gguf 2>/dev/null | head -n1)"
TPL="$D/chat_template.jinja"
HELP="$("$BIN" --help 2>&1 || true)"
OPT=()
case "$HELP" in *--reasoning-effort*) OPT+=(--reasoning-effort medium);; *) OPT+=(--chat-template-kwargs '{"reasoning_effort":"medium"}');; esac
HAS_SPEC=0; case "$HELP" in *--spec-type*) HAS_SPEC=1;; esac
SPEC=(); if [ -n "$MTP" ] && [ "$HAS_SPEC" = 1 ]; then SPEC=(-md "$MTP" --spec-type draft-mtp); fi
MMF=(); if [ -n "$MM" ]; then MMF=(--mmproj "$MM"); fi
TPLF=(); if [ -f "$TPL" ]; then TPLF=(--chat-template-file "$TPL"); fi
BASE=(-m "$MAIN" -ngl 99 --jinja "${TPLF[@]}" "${MMF[@]}" "${SPEC[@]}" "${OPT[@]}" --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0 --repeat-penalty 1.0 --presence-penalty 0.0 --frequency-penalty 0.0 --host 127.0.0.1 --port 8080)
for CFG in "262144:" "262144:q8_0" "131072:q8_0" "65536:q8_0"; do
    CTX="${CFG%%:*}"; KV="${CFG##*:}"
    KVARGS=(); if [ -n "$KV" ]; then KVARGS=(-ctk "$KV" -ctv "$KV"); fi
    echo "[launcher] ctx=$CTX kv=${KV:-f16}"
    START=$SECONDS
    "$BIN" "${BASE[@]}" "${KVARGS[@]}" --ctx-size "$CTX"
    RC=$?
    if [ $((SECONDS-START)) -gt 120 ]; then exit $RC; fi
    echo "[launcher] exit $RC на загрузке; следующая конфигурация"
done
exit 1
SH
chmod 755 /opt/ivc_ai/run-llama-server.sh
cat > /etc/systemd/system/llama-server.service <<EOF
[Unit]
Description=ivc_ai llama-server (NanoPlus, full GPU offload, MTP draft)
After=network-online.target
Wants=network-online.target
ConditionPathExistsGlob=/opt/ivc_ai/models/*.gguf

[Service]
Type=simple
User=$REAL_USER
Group=$REAL_USER
ExecStart=/bin/bash /opt/ivc_ai/run-llama-server.sh
Restart=on-failure
RestartSec=5
Nice=-5

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable llama-server
if ls /opt/ivc_ai/models/*.gguf >/dev/null 2>&1; then
    systemctl start llama-server
    ok=0
    for i in $(seq 1 100); do
        if curl -sf --max-time 3 http://127.0.0.1:8080/health >/dev/null; then ok=1; break; fi
        sleep 3
    done
    if [ "$ok" = 1 ]; then echo "[+] llama-server здоров: http://127.0.0.1:8080"; else echo "[!] Не поднялся за 300с: journalctl -u llama-server -n 50"; fi
else
    echo "[+] Модели нет - юнит включён, старт после появления gguf: systemctl start llama-server"
fi

# 13. Финал
ip -br addr || true
echo "[i] IP сервера: $(hostname -I)"
echo "[i] DHCP меняется - закрепите аренду на роутере."
echo "[i] Клиент: ssh -L 8080:127.0.0.1:8080 $REAL_USER@<IP>, затем http://127.0.0.1:8080"
echo "=== ЭТАП Б ЗАВЕРШЁН ==="
echo "Перелогиньтесь (newgrp docker) для группы docker и PATH nvm/pnpm/uv."
```

## Что проверяется автоматически
- Сеть/зеркала, keyring, pinning-пакет, nvcc, nvidia-smi, dkms status
- Ключевой вход подтверждается вручную до отключения паролей; sshd -t; TCP к sshd после reload
- LV/монтирования, защита бэкапа home; место >20 ГБ; размер main gguf >10 ГБ
- llama-cli --version; swapon; docker --version; llama-server /health до 300 с

## Связи
- [[01_BIOS_Preparation]]
- [[02_Debian_Installation]]
- [[03_System_Configuration]]
- [[04_NVIDIA_Drivers]]
- [[05_AI_Tools_Setup]]
- [[06_Network_Fix_USB_Modem]]
- [[08_Hardware_Profile]]
- [[09_Client_File_Delivery]]
