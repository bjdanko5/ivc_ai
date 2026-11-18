---
type: project
project: ivc_ai
tags: [ivc_ai, local_ai]
---

# ivc_ai

Vault + Git + code + checks.

## Security rule

Never store passwords/tokens in this vault.
Secrets live in KeePassXC and local .env (git-ignored).
In notes write only a reference, e.g.: HF token -> KeePassXC entry `hf-token`.

## Folders

00_Inbox raw input | 10_Projects project notes | 20_Knowledge distilled how-tos
30_Chats AI chat archive (strip secrets first!) | 40_Cards script cards
90_Templates templates | code/scripts cmd+ps1 | code/py python | tools checks | logs reports

## Commands

Check:  py -3 tools\ivc_check.py
Commit: py -3 tools\ivc_git_sync.py -m "update"
Push:   py -3 tools\ivc_git_sync.py -m "update" --push
