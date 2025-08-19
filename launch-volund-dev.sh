#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ==============================================================
# VOLUND - Développement (Linux/Fedora)
# Port du launchdev.bat → bash
# ==============================================================

set -Eeuo pipefail
IFS=$'\n\t'

# --- Aller dans le répertoire du script ---
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Journalisation ---
LOGFILE="/tmp/volund_launcher_log.txt"
echo "[LOG] Journalisation dans $LOGFILE"
{
  echo "Lancement : $(date '+%Y-%m-%d %H:%M:%S')"
  echo "Script   : $0"
  echo "Dossier  : $SCRIPT_DIR"
} > "$LOGFILE"

# --- Titre de la fenêtre (si terminal compatible) ---
printf "\033]0;VOLUND - Développement\007" || true

# --- Bannière ---
cat <<'BANNER'
==================================================================

:::     :::  ::::::::  :::       :::    ::: ::::    ::: :::::::::  
:+:     :+: :+:    :+: :+:       :+:    :+: :+:+:   :+: :+:    :+:
+:+     +:+ +:+    +:+ +:+       +:+    +:+ :+:+:+  +:+ +:+    +:+ 
+#+     +:+ +#+    +:+ +#+       +#+    +:+ +#+ +:+ +#+ +#+    +:+ 
 +#+   +#+  +#+    +#+ +#+       +#+    +#+ +#+  +#+#+# +#+    +#+ 
  #+#+#+#   #+#    #+# #+#       #+#    #+# #+#   #+#+# #+#    #+# 
    ###      ########  ########## ########  ###    #### #########  

                   VOLUND DEV - Let's build 💻✨

==================================================================
BANNER

# === [1] POSITION MANUELLE (désactivée) ===
# NOTE: le déplacement de fenêtre n'est pas standard en bash; laissé de côté.

# === [2] LANCEMENT DE VØLUND ===

# --- Vérifie si un VPN est actif (nmcli) ---
echo "[CHECK] Vérification VPN..."
if command -v nmcli >/dev/null 2>&1; then
  if nmcli -t -f NAME,TYPE,DEVICE con show --active | grep -iE '\bvpn\b' >/dev/null 2>&1; then
    echo "[ALERTE] Un VPN semble actif. Cela peut bloquer certaines fonctionnalités." | tee -a "$LOGFILE"
  else
    echo "[CHECK] Aucun VPN détecté." | tee -a "$LOGFILE"
  fi
else
  echo "[INFO] nmcli indisponible, saut du check VPN." | tee -a "$LOGFILE"
fi

# --- Vérification & lancement d'Ollama ---
echo "--------------------------------------------------"
echo "[SYS] Vérification d'Ollama (localhost:11434)"
echo "--------------------------------------------------"

if ! command -v ollama >/dev/null 2>&1; then
  echo "❌ [ERREUR] Ollama introuvable dans le PATH." | tee -a "$LOGFILE"
  echo "👉 Installe-le puis relance (https://ollama.ai)." | tee -a "$LOGFILE"
else
  # Démarre ollama serve si pas déjà présent
  if pgrep -f "ollama serve" >/dev/null 2>&1; then
    echo "✅ [SYS] Ollama déjà actif." | tee -a "$LOGFILE"
  else
    echo "[SYS] Démarrage d'Ollama..." | tee -a "$LOGFILE"
    OLLAMA_DEBUG=0 nohup ollama serve >/dev/null 2>&1 &
    sleep 2
  fi

  # Vérifie le port
  echo "[SYS] Vérification du port 11434..." | tee -a "$LOGFILE"
  if ss -lnt 2>/dev/null | grep -q ":11434\b"; then
    echo "✅ [SYS] Port 11434 ouvert." | tee -a "$LOGFILE"
  else
    echo "⚠️  [SYS] Port 11434 non ouvert." | tee -a "$LOGFILE"
  fi

  # Précharge le modèle codellama (silencieux)
  echo "[SYS] Préchargement modèle codellama..." | tee -a "$LOGFILE"
  curl -s -X POST http://127.0.0.1:11434/api/generate \
    -H 'Content-Type: application/json' \
    -d '{"model":"codellama:13b-instruct","prompt":"ping","stream":false}' >/dev/null \
    && echo "✅ [SYS] Modèle codellama préchargé." | tee -a "$LOGFILE" \
    || echo "❌ [SYS] Échec du préchargement codellama." | tee -a "$LOGFILE"
fi

echo "✅ [SYS] Vérification Ollama terminée." | tee -a "$LOGFILE"

# --- Lancement de l'IDE (Cursor si dispo, sinon VS Code) ---
echo "[IDE] Lancement IDE..." | tee -a "$LOGFILE"
if command -v cursor >/dev/null 2>&1; then
  echo "✅ [IDE] Cursor détecté." | tee -a "$LOGFILE"
  (cursor "$SCRIPT_DIR" >/dev/null 2>&1 &)
elif command -v code >/dev/null 2>&1; then
  echo "✅ [IDE] VS Code détecté." | tee -a "$LOGFILE"
  (code "$SCRIPT_DIR" >/dev/null 2>&1 &)
else
  echo "⚠️  [IDE] Aucun IDE (cursor/code) trouvé dans le PATH." | tee -a "$LOGFILE"
fi

# --- Lancement du script Python ---
echo "[PY] Vérification de l'environnement Python..." | tee -a "$LOGFILE"
PY_BIN=".venv/bin/python"
if [[ -x "$PY_BIN" ]]; then
  echo "[PY] Environnement Python détecté." | tee -a "$LOGFILE"
  if "$PY_BIN" dev_launcher.py; then
    echo "✅ Script Python exécuté sans erreur." | tee -a "$LOGFILE"
  else
    echo "❌ [PY] Erreur dans dev_launcher.py." | tee -a "$LOGFILE"
  fi
else
  echo "❌ [ERREUR] Python non trouvé dans .venv." | tee -a "$LOGFILE"
  echo "❌ Environnement virtuel manquant ou incorrect." | tee -a "$LOGFILE"
fi

# --- Relance optionnelle ---
read -r -p $'Souhaitez-vous relancer Vølund ? (o/n) : ' userinput || true
if [[ "${userinput:-n}" =~ ^[oOyY]$ ]]; then
  exec "$0"
fi

# --- Fin ---
echo
echo "🔍 Fin du script. Consulte le journal ici : $LOGFILE"
echo

