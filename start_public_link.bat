@echo off
title BugFlow Live Server & Public Link
cd /d "%~dp0"
echo ============================================================
echo   ?? Starting BugFlow Web Server on http://127.0.0.1:8000
echo ============================================================
start "BugFlow Server" cmd /k "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul
echo ============================================================
echo   ?? Starting Cloudflare Public Tunnel...
echo ============================================================
cloudflared.exe tunnel --url http://127.0.0.1:8000
pause
