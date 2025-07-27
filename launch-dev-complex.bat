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

:: Vérifie si WSL est disponible
where wsl > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ [ERREUR] WSL non disponible. >> %LOGFILE%
    echo ❌ WSL non détecté sur cette machine.
    goto FIN
)

:: Vérifie si Ollama tourne via WSL
echo [WSL] Vérification d'Ollama...
wsl ps aux | findstr /I "ollama serve" >> %LOGFILE%
if %errorlevel%==1 (
    echo [WSL] Ollama non détecté, tentative de lancement...
    echo Lancement Ollama... >> %LOGFILE%
    wsl -e bash -c "OLLAMA_DEBUG=0 nohup ollama serve > /dev/null 2>&1 &"
    if %errorlevel% neq 0 (
        echo ❌ [ERREUR] Échec du lancement d'Ollama. >> %LOGFILE%
    ) else (
        echo ✅ [WSL] Ollama lancé. >> %LOGFILE%
    )
) else (
    echo ✅ [WSL] Ollama déjà en cours. >> %LOGFILE%
)

:: Test du endpoint Ollama pour forcer un preload
echo [WSL] Préchargement modèle codellama...
wsl -e bash -c "curl -s http://127.0.0.1:11434/api/generate -d '{\"model\": \"codellama:13b-instruct\", \"prompt\": \"ping\", \"stream\": false}' > /dev/null"
if %errorlevel% neq 0 (
    echo ⚠️ [WSL] Erreur pendant le preload du modèle. >> %LOGFILE%
) else (
    echo ✅ [WSL] Modèle préchargé. >> %LOGFILE%
)

:: === [WIN] LANCEMENT VS CODE CLASSIQUE (PAS CURSOR) ===
echo [WIN] Lancement de VS Code...

:: Sauvegarde du répertoire courant
set "PROJECT_DIR=%cd%"

:: Emplacement typique de VS Code (hors Cursor)
set "VSCODE_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe"

if exist "%VSCODE_PATH%" (
    echo ✅ [WIN] VS Code trouvé à %VSCODE_PATH%. >> %LOGFILE%
    start "" "%VSCODE_PATH%" "%PROJECT_DIR%"
    echo ✅ [WIN] VS Code lancé. >> %LOGFILE%
) else (
    echo ❌ [ERREUR] VS Code non trouvé à l’emplacement attendu. >> %LOGFILE%
    echo ❌ [INFO] Tu peux corriger le chemin dans le script si besoin.
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
