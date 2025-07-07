@echo off
chcp 65001 > nul
title Génération d'un module Vølund
cd /d "%~dp0"

:: Chemin vers le script
set SCRIPT=GenerateModule.py

:: Vérifie que Python est bien là
if exist .venv\Scripts\python.exe (
    echo ✅ Environnement virtuel détecté.
    echo 🚀 Lancement de la génération du module...
    .venv\Scripts\python.exe %SCRIPT%
) else (
    echo ❌ Python non trouvé dans .venv\Scripts\python.exe
    echo 🔧 Merci d’activer ou recréer l’environnement virtuel.
)

echo.
echo ✅ Terminé. Appuie sur une touche pour fermer cette fenêtre.
pause > nul
