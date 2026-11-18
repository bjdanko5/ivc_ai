#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Full vault check: structure, git, python syntax, secrets."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
problems = []

def ok(msg): print("[OK]", msg)
def bad(msg): problems.append(msg); print("[PROBLEM]", msg)

for d in ["00_Inbox", "10_Projects", "20_Knowledge", "30_Chats", "40_Cards",
          "90_Templates", "code/scripts", "code/py", "tools"]:
    (ok if (ROOT / d).is_dir() else bad)("dir " + d)

if (ROOT / ".git").is_dir(): ok("git repo")
else: bad("no git repo (run setup)")

gi = ROOT / ".gitignore"
if gi.is_file():
    t = gi.read_text(encoding="utf-8")
    for rule in [".env", "*.kdbx", "__pycache__/", "logs/"]:
        (ok if rule in t else bad)(".gitignore " + rule)
else:
    bad("no .gitignore")

for p in ROOT.rglob("*.py"):
    if any(x in p.parts for x in (".venv", "venv", "__pycache__")):
        continue
    r = subprocess.run([sys.executable, "-m", "py_compile", str(p)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (ok if r.returncode == 0 else bad)("python " + p.name)

r = subprocess.run([sys.executable, str(ROOT / "tools" / "ivc_secret_scan.py"),
                    "--root", str(ROOT)] + (["--staged"] if "--staged" in sys.argv else []))
if r.returncode != 0: bad("SECRET SCAN FAILED")

print()
if problems:
    print("RESULT: %d problem(s)" % len(problems)); sys.exit(1)
print("RESULT: ALL OK")
