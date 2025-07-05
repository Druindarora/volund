@echo off
title VOLUND - Développement
cd /d "%~dp0"

REM Utilise directement le python du .venv (sans activer de session)
call .venv\Scripts\python.exe dev_launcher.py

REM Garde la console ouverte après exécution
echo.
pause
