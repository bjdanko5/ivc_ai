@echo off
chcp 65001 >nul
cd /d C:\ivc_ai
git add -A
for /f %%i in ('git diff --cached --name-only') do set CHANGED=1
if defined CHANGED (
    git commit -m "vault backup: %date% %time%"
    git push origin main 2>nul
    echo [OK] committed and pushed
) else (
    echo [OK] nothing to commit
)
