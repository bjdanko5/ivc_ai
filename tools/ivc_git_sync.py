#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check -> add -> staged check -> commit -> optional push"""
import argparse, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(cmd):
    r = subprocess.run(cmd, cwd=str(ROOT))
    if r.returncode != 0:
        print("[STOP] failed:", " ".join(cmd)); sys.exit(1)

ap = argparse.ArgumentParser()
ap.add_argument("-m", "--message", default="ivc_ai update")
ap.add_argument("--push", action="store_true")
a = ap.parse_args()

run([sys.executable, "tools/ivc_check.py"])
run(["git", "add", "-A"])
run([sys.executable, "tools/ivc_check.py", "--staged"])

st = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=str(ROOT),
                    stdout=subprocess.PIPE, universal_newlines=True).stdout.strip()
if not st:
    print("[OK] nothing to commit"); sys.exit(0)

run(["git", "commit", "-m", a.message])
if a.push:
    run(["git", "push", "-u", "origin", "main"])
print("[DONE]")
