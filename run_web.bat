@echo off
title AI Shorts Maker - Web UI
echo ========================================================
echo   Iniciando AI Shorts Maker no Navegador...
echo ========================================================
cd /d "%~dp0"
.\.venv\Scripts\python.exe app.py
pause
