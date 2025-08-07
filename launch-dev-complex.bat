@echo off
chcp 65001 > nul
title VOLUND - Développement
cd /d "%~dp0"

:: Crée un log temporaire
set LOGFILE="%TEMP%\volund_launcher_log.txt"
echo [LOG] Journalisation dans %LOGFILE%
echo Lancement : %DATE% %TIME% > %LOGFILE%

echo ==================================================================
echo.
echo :::     :::  ::::::::  :::       :::    ::: ::::    ::: :::::::::  
echo :+:     :+: :+:    :+: :+:       :+:    :+: :+:+:   :+: :+:    :+: 
echo +:+     +:+ +:+    +:+ +:+       +:+    +:+ :+:+:+  +:+ +:+    +:+ 
echo +#+     +:+ +#+    +:+ +#+       +#+    +:+ +#+ +:+ +#+ +#+    +:+ 
echo  +#+   +#+  +#+    +#+ +#+       +#+    +#+ +#+  +#+#+# +#+    +#+ 
echo   #+#+#+#   #+#    #+# #+#       #+#    #+# #+#   #+#+# #+#    #+# 
echo     ###      ########  ########## ########  ###    #### #########  
echo.
echo                    VOLUND DEV - Let's build 💻✨
echo.
echo ==================================================================
echo.

:: === [1] POSITION MANUELLE (désactivée par défaut) ===
:: === Position actuelle : X=-967, Y=0, Largeur=974, Hauteur=1039
:: Position actuelle : X=-2887, Y=-693, Largeur=974, Hauteur=1039
powershell -ExecutionPolicy Bypass -File "move_console.ps1"

:: === [2] LANCEMENT DE VØLUND ===


:: Vérifie si un VPN est actif
echo [CHECK] Vérification VPN...
ipconfig | findstr /I "ExpressVPN" >> %LOGFILE%
if %errorlevel%==0 (
    echo [WARN] VPN détecté. >> %LOGFILE%
    echo [ALERTE] Un VPN semble actif. Cela peut bloquer WSL, VS Code ou Ollama.
) else (
    echo [CHECK] Aucun VPN détecté. >> %LOGFILE%
)

:: === [WSL] VÉRIFICATION & LANCEMENT OLLAMA ===
echo --------------------------------------------------
echo [WSL] Vérification de WSL et du serveur Ollama...
echo --------------------------------------------------

:: Vérifie si WSL est dispo
where wsl > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ [ERREUR] WSL non disponible.
    echo ❌ [ERREUR] WSL non disponible. >> %LOGFILE%
    goto FIN
)

:: Vérifie si Ollama tourne déjà
wsl ps aux | findstr /I "ollama serve" > nul
if %errorlevel%==1 (
    echo [WSL] Ollama non détecté. Lancement...
    echo [WSL] Ollama non détecté. Lancement... >> %LOGFILE%

    wsl -e bash -c "OLLAMA_DEBUG=0 nohup ollama serve > /dev/null 2>&1 &"
    timeout /t 2 > nul
) else (
    echo ✅ [WSL] Ollama semble déjà actif.
    echo ✅ [WSL] Ollama semble déjà actif. >> %LOGFILE%
)

:: Vérifie si le port est ouvert
echo [WSL] Vérification du port 11434...
wsl -e bash -c "netstat -an | grep 11434" > nul
if %errorlevel% neq 0 (
    echo ⚠️ [WSL] Port 11434 non ouvert.
    echo ⚠️ [WSL] Port 11434 non ouvert. >> %LOGFILE%
) else (
    echo ✅ [WSL] Port 11434 ouvert.
    echo ✅ [WSL] Port 11434 ouvert. >> %LOGFILE%
)

:: Ping du modèle pour forcer un preload
echo [WSL] Préchargement modèle codellama...
wsl -e bash -c "curl -s -X POST http://127.0.0.1:11434/api/generate -H 'Content-Type: application/json' -d '{\"model\": \"codellama:13b-instruct\", \"prompt\": \"ping\", \"stream\": false}' > /dev/null"

if %errorlevel% neq 0 (
    echo ❌ [ERREUR] Échec du preload modèle codellama.
    echo ❌ [ERREUR] Échec du preload modèle codellama. >> %LOGFILE%
) else (
    echo ✅ [WSL] Modèle codellama préchargé avec succès.
    echo ✅ [WSL] Modèle codellama préchargé avec succès. >> %LOGFILE%
)

echo ✅ [WSL] Vérification complète terminée.
echo ✅ [WSL] Vérification complète terminée. >> %LOGFILE%


:: === [WIN] LANCEMENT VS CODE CLASSIQUE (PAS CURSOR) ===
echo [WIN] Lancement de VS Code...

:: Sauvegarde du répertoire courant
set "PROJECT_DIR=%cd%"

:: Emplacement typique de Cursor IDE
set "CURSOR_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe"

if exist "%CURSOR_PATH%" (
    echo ✅ [WIN] Cursor trouvé à %CURSOR_PATH%. >> %LOGFILE%
    start "" "%CURSOR_PATH%" "%PROJECT_DIR%"
    echo ✅ [WIN] Cursor lancé. >> %LOGFILE%
) else (
    echo ❌ [ERREUR] Cursor non trouvé à l’emplacement attendu. >> %LOGFILE%
    echo ❌ [INFO] Corrige le chemin si Cursor est ailleurs.
)


:: Lancement du script Python
if exist .venv\Scripts\python.exe (
    echo [PY] Environnement Python détecté.

    .venv\Scripts\python.exe dev_launcher.py

    if errorlevel 1 (
        goto PY_FAIL
    ) else (
        goto PY_OK
    )
) else (
    goto PY_NOT_FOUND
)

:PY_OK
echo ✅ Script Python exécuté sans erreur. >> %LOGFILE%
goto PY_DONE

:PY_FAIL
echo ❌ [PY] Erreur dans dev_launcher.py. >> %LOGFILE%
echo ❌ Une erreur s'est produite dans le script Python.
goto PY_DONE

:PY_NOT_FOUND
echo ❌ [ERREUR] Python non trouvé dans .venv. >> %LOGFILE%
echo ❌ Environnement virtuel manquant ou incorrect.
goto PY_DONE

:PY_DONE
@REM echo Appuie sur une touche pour continuer... fin du Python
@REM pause > nul

@REM REM ============================
@REM REM === [3] POSITION ACTUELLE DE LA FENÊTRE
@REM echo.
@REM echo [POSITION] Lecture de la position actuelle de la console...
@REM powershell -ExecutionPolicy Bypass -File "%~dp0get_console_position.ps1"


REM ============================
REM === [4] RELANCE OPTIONNELLE
:ask_restart
set /p userinput=Souhaitez-vous relancer Vølund ? (o/n) :
if /i "%userinput%"=="o" goto relaunch
if /i "%userinput%"=="n" goto end
goto ask_restart

:relaunch
cls
call "%~f0"
goto :eof

:FIN
echo.
echo 🔍 Fin du script. Consulte le journal ici : %LOGFILE%
echo.
echo 🔎 Appuie sur une touche pour fermer...
pause > nul
