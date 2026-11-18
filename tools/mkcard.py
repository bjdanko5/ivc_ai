#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mkcard.py - create script card + empty script file in one command.

Usage:
    py -3 tools/mkcard.py <script_name> <lang> [description]

Examples:
    py -3 tools/mkcard.py backup_vault cmd "Backup vault to external drive"
    py -3 tools/mkcard.py convert_chats py "Convert ChatGPT export to md"
"""
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXT_MAP = {"py": ".py", "cmd": ".cmd", "bat": ".bat", "ps1": ".ps1",
           "bash": ".sh", "sh": ".sh"}


def main():
    if len(sys.argv) < 3:
        print("Usage: py -3 tools/mkcard.py <name> <lang> [description]")
        print("Example: py -3 tools/mkcard.py backup_vault cmd")
        sys.exit(1)

    name = sys.argv[1]
    lang = sys.argv[2].lower()
    desc = sys.argv[3] if len(sys.argv) > 3 else ""
    today = date.today().isoformat()
    ext = EXT_MAP.get(lang, "." + lang)

    card_path = ROOT / "40_Cards" / (name + ".md")
    script_rel = "code/scripts/" + name + ext
    script_path = ROOT / script_rel

    if card_path.exists():
        print("[skip] card exists: " + str(card_path.relative_to(ROOT)))
        sys.exit(0)

    card_lines = [
        "---",
        "type: script",
        "project: ivc_ai",
        "lang: " + lang,
        "path: " + script_rel,
        "created: " + today,
        "tags: [script, ivc_ai]",
        "---",
        "",
        "# " + name.replace("_", " ").title(),
        "",
        "## Purpose",
        "",
        desc,
        "",
        "## Location",
        "",
        "`" + script_rel + "`",
        "",
        "## Run",
        "",
        "```" + lang,
        "",
        "```",
        "",
        "## Dependencies",
        "",
        "",
        "## Secrets",
        "",
        "No values here. Reference: KeePassXC entry `name`.",
        "",
        "## Verified",
        "",
        "- [ ] runs ok",
        "- [ ] no secrets",
        "- [ ] committed",
        "",
    ]
    card_path.parent.mkdir(parents=True, exist_ok=True)
    card_path.write_text("\n".join(card_lines), encoding="utf-8")
    print("[new] " + str(card_path.relative_to(ROOT)))

    if not script_path.exists():
        script_path.parent.mkdir(parents=True, exist_ok=True)
        if lang == "py":
            header = "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n"
            header += '"""' + desc + '"""\n\n'
        elif lang in ("cmd", "bat"):
            header = "@echo off\nrem " + name + " - " + desc + "\nrem Created: " + today + "\n\n"
        elif lang in ("bash", "sh"):
            header = "#!/bin/bash\n# " + name + " - " + desc + "\n# Created: " + today + "\n\n"
        elif lang == "ps1":
            header = "# " + name + " - " + desc + "\n# Created: " + today + "\n\n"
        else:
            header = "# " + name + " - " + desc + "\n# Created: " + today + "\n\n"
        script_path.write_text(header, encoding="utf-8")
        print("[new] " + str(script_path.relative_to(ROOT)))
    else:
        print("[skip] script exists: " + str(script_path.relative_to(ROOT)))


if __name__ == "__main__":
    main()
