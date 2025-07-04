@echo off
title VOLUND - Développement

REM Active l'environnement virtuel
call .venv\Scripts\activate.bat

REM Lance le script de dev avec redémarrage auto
REM /K garde la console ouverte après l'exécution
cmd /K python dev_launcher.py
