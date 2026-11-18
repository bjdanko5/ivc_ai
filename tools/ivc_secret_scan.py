#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Secret scanner. --staged scans git index only, default scans whole vault."""
import argparse, datetime, json, os, re, subprocess, sys
from pathlib import Path

PATTERNS = [
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("hf-token", re.compile(r"\bhf_[A-Za-z0-9]{30,}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("github-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b")),
    ("aws-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private-key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("password-assign", re.compile(
        r"(?i)\b(password|passwd|pwd|token|api[_-]?key|secret)\b[ \t]*[:=][ \t]*['\"]?[A-Za-z0-9_./+=-]{8,}")),
]
SKIP = {".git", ".venv", "venv", "__pycache__", "logs", ".trash", "node_modules"}
TEXT = {".md", ".txt", ".py", ".ps1", ".cmd", ".bat", ".json", ".yaml", ".yml",
        ".toml", ".ini", ".cfg", ".csv", ".html", ".js", ".sh", ""}
BAD_EXT = {".kdbx", ".key", ".pem", ".p12", ".pfx"}
BAD_NAMES = {".env", "token.txt", "tokens.txt", "credentials.json"}

def git(root, *args):
    p = subprocess.run(["git", "-C", str(root)] + list(args),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return p.returncode, (p.stdout + p.stderr).strip()

def mask(s):
    return s[:3] + "***" if len(s) <= 12 else s[:6] + "..." + s[-4:]

def scan_text(text):
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        if re.match(r"(?i)^[A-Z0-9_]*(TOKEN|KEY|PASSWORD|SECRET)[A-Z0-9_]*=\s*$", line.strip()):
            continue
        for name, pat in PATTERNS:
            for m in pat.finditer(line):
                v = m.group(0)
                if any(x in v.lower() for x in ("example", "changeme", "placeholder", "your_token")):
                    continue
                hits.append((name, n, mask(v)))
    return hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--staged", action="store_true")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    findings = []

    rc, out = git(root, "ls-files")
    if rc == 0:
        for rel in out.splitlines():
            p = Path(rel.strip())
            nm = p.name.lower()
            if nm in BAD_NAMES or (nm.startswith(".env.") and nm != ".env.example") \
               or p.suffix.lower() in BAD_EXT \
               or any(x.lower() in ("secrets", "private", "credentials") for x in p.parts):
                findings.append(("tracked-secret-file", rel.strip(), 0, "remove: git rm --cached"))

    if a.staged:
        rc, out = git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMRT")
        paths = [root / x.strip() for x in out.splitlines() if x.strip()]
    else:
        paths = []
        for dp, dns, fns in os.walk(str(root)):
            dns[:] = [d for d in dns if d not in SKIP]
            paths += [Path(dp) / f for f in fns]

    for p in paths:
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(root)
        except ValueError:
            continue
        if any(x in SKIP for x in rel.parts):
            continue
        nm = p.name.lower()
        if nm == ".env" or (nm.startswith(".env.") and nm != ".env.example"):
            continue
        if p.suffix.lower() not in TEXT or p.stat().st_size > 2000000:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for name, n, sample in scan_text(text):
            findings.append((name, str(rel).replace("\\", "/"), n, sample))

    logs = root / "logs"
    logs.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report = logs / ("scan_" + stamp + ".json")
    report.write_text(json.dumps(findings, indent=2), encoding="utf-8")

    if findings:
        print("[BLOCK] potential secrets found:")
        for name, f, n, s in findings:
            print("  %s:%s  %s  %s" % (f, n, name, s))
        print("report:", report)
        print("Fix: move secret to KeePassXC, then re-run.")
        return 1
    print("[OK] no secrets. report:", report)
    return 0

if __name__ == "__main__":
    sys.exit(main())
