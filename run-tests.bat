@echo off
title ▶ Tests Vølund

REM === Se placer à la racine du projet
cd /d "%~dp0"

REM === Activer l'environnement virtuel
call .venv\Scripts\activate.bat

REM === Définir le PYTHONPATH pour les imports depuis src/
set PYTHONPATH=src

REM === Lancer les tests avec pytest depuis PowerShell
powershell -NoExit -Command "pytest --tb=short --cov=src/modules/parlia --cov-report=term-missing --cov-report=html"
