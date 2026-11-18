#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mknote.py - quick note creator for ivc_ai vault.

Usage:
    py -3 tools/mknote.py <relative_path> [title]

Examples:
    py -3 tools/mknote.py 20_Knowledge/ollama_setup.md
    py -3 tools/mknote.py 40_Cards/backup_script.md "Backup Script Card"
    py -3 tools/mknote.py 00_Inbox/raw_idea.md

Creates file with YAML frontmatter if not exists.
Skips existing files (never overwrites).
"""
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def guess_type(rel: str) -> str:
    parts = rel.lower().split("/")
    if "cards" in parts or "card" in rel.lower():
        return "script"
    if "chats" in parts:
        return "chat"
    if "projects" in parts:
        return "project"
    return "knowledge"

def make_frontmatter(rel: str, title: str) -> str:
    ntype = guess_type(rel)
    today = date.today().isoformat()
    tag = ntype
    lines = [
        "---",
        f"type: {ntype}",
        "project: ivc_ai",
    ]
    if ntype == "knowledge":
        lines.append("topic: ")
    if ntype == "script":
        lines += ["lang: ", "path: "]
    if ntype == "chat":
        lines += ["source: ", "model: "]
    lines += [
        f"created: {today}",
        f"tags: [{tag}, ivc_ai]",
        "---",
        "",
        f"# {title}",
        "",
    ]
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: py -3 tools/mknote.py <relative_path> [title]")
        print("Example: py -3 tools/mknote.py 20_Knowledge/ollama_setup.md")
        sys.exit(1)

    rel = sys.argv[1].replace("\\", "/")
    if not rel.endswith(".md"):
        rel += ".md"

    p = ROOT / rel
    if p.exists():
        print(f"[skip] already exists: {rel}")
        sys.exit(0)

    title = sys.argv[2] if len(sys.argv) > 2 else p.stem.replace("_", " ").title()

    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(make_frontmatter(rel, title), encoding="utf-8")
    print(f"[new] {rel}")

if __name__ == "__main__":
    main()
