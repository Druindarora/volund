@echo off
echo Lancement du serveur Whisper avec uvicorn...
E:\dev\Projets\Volund\.venv\Scripts\uvicorn.exe whisper_server:app --host 127.0.0.1 --port 5005
pause
