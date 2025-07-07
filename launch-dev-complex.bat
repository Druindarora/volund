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

:: Lancement de VS Code
echo [WIN] Lancement de VS Code...
:: Sauvegarde du répertoire courant dans une variable protégée
set "PROJECT_DIR=%cd%"

:: Vérifie que la commande 'code' est disponible
where code > nul 2>&1
set CODE_AVAILABLE=%errorlevel%

echo CODE_AVAILABLE=%CODE_AVAILABLE%

if not defined CODE_AVAILABLE (
    echo ❌ Variable CODE_AVAILABLE non définie ! >> %LOGFILE%
    echo ❌ Erreur inattendue : CODE_AVAILABLE est vide.
    goto FIN
)

if "%CODE_AVAILABLE%"=="0" goto CODE_OK
goto CODE_NOT_FOUND

:CODE_OK
echo ✅ VS Code est disponible.
call code "%PROJECT_DIR%" >> %LOGFILE% 2>&1
set CODE_LAUNCH_STATUS=%errorlevel%
goto CODE_DONE

:CODE_NOT_FOUND
echo ❌ [ERREUR] VS Code introuvable. >> %LOGFILE%
echo ❌ La commande 'code' n’est pas dans le PATH.
goto CODE_DONE

:CODE_DONE

:: Lancement du script Python
if exist .venv\Scripts\python.exe (
    echo [PY] Environnement Python détecté.

    .venv\Scripts\python.exe dev_launcher.py >> %LOGFILE% 2>&1

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
echo Appuie sur une touche pour continuer... fin du Python
pause > nul



:FIN
echo.
echo 🔍 Fin du script. Consulte le journal ici : %LOGFILE%
echo.
echo 🔎 Appuie sur une touche pour fermer...
pause > nul
