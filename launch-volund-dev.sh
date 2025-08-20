#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ==============================================================
# VOLUND - Développement (Linux/Fedora)
# Port du launchdev.bat → bash (nettoyé)
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
# NOTE: sous Linux, déplacer/positionner une fenêtre depuis bash n’est pas portable.
#       Il faudrait des outils du WM (wmctrl/xdotool) et c’est fragile → laissé de côté.

# === [2] LANCEMENT DE L'IDE (détaché du terminal) ===
echo "[IDE] Lancement IDE..." | tee -a "$LOGFILE"
if command -v cursor >/dev/null 2>&1; then
  echo "✅ [IDE] Cursor détecté." | tee -a "$LOGFILE"
  nohup cursor "$SCRIPT_DIR" >/dev/null 2>&1 & disown || true
elif command -v code >/dev/null 2>&1; then
  echo "✅ [IDE] VS Code détecté." | tee -a "$LOGFILE"
  nohup code "$SCRIPT_DIR" >/dev/null 2>&1 & disown || true
else
  echo "⚠️  [IDE] Aucun IDE (cursor/code) trouvé dans le PATH." | tee -a "$LOGFILE"
fi

# === [3] LANCEMENT DE VØLUND (Python) ===
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
  # chemin absolu du dossier courant du script
  SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  BASE_NAME="$(basename -- "${BASH_SOURCE[0]}")"

  # ⬇️ si un script "batch-<nom>" existe, on privilégie celui-là
  TARGET="${SCRIPT_DIR}/batch-${BASE_NAME}"
  if [[ ! -f "$TARGET" ]]; then
    TARGET="${SCRIPT_DIR}/${BASE_NAME}"
  fi

  # ⚠️ évite les pb de permission en relançant via bash explicitement
  exec /usr/bin/env bash "$TARGET"
fi

# --- Fin ---
echo
echo "🔍 Fin du script. Consulte le journal ici : $LOGFILE"
echo
