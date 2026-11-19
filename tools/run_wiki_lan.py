import socket
import subprocess
import sys
import time
from pathlib import Path

SETUP = Path(r'C:\ivc_ai\20_Knowledge\Server_Setup')

def free_port(start):
    for p in range(start, start + 200):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', p))
                return p
            except OSError:
                continue
    return None

try:
    for attempt in range(1, 6):
        port = free_port(4000)
        if port is None:
            print('No free port in 4000-4200')
            sys.exit(1)
        print(f'[{attempt}] Site: http://192.168.11.218:{port}  (Ctrl+C to stop)')
        rc = subprocess.run(
            [sys.executable, '-m', 'mkdocs', 'serve', '-a', f'0.0.0.0:{port}'],
            cwd=SETUP,
        ).returncode
        if rc == 0:
            break
        print(f'mkdocs exited {rc}; retry in 3 s...')
        time.sleep(3)
except KeyboardInterrupt:
    print('\nServer stopped.')
