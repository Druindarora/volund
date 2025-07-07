import io
import os
import subprocess
import sys
import time

# Forcer la sortie console en UTF-8 (s'il est compatible)
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

USE_EMOJI = "TERM_PROGRAM" in os.environ or "WT_SESSION" in os.environ


def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode())


safe_print(f"{'🔍' if USE_EMOJI else '[INFO]'} Python utilisé : {sys.executable}")

print(f"🔍 Python utilisé : {sys.executable}")

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

SCRIPT_PATH = os.path.join("src", "main.py")
SRC_DIR = "src"

# Chemin vers ruff dans l’environnement virtuel
# RUFF_PATH = os.path.join(os.environ["VIRTUAL_ENV"], "Scripts", "ruff.exe")
RUFF_PATH = os.path.join(os.path.dirname(sys.executable), "ruff.exe")
print(f"🧪 Ruff path prévu : {RUFF_PATH}")
print(f"🧪 Ruff existe ? {'✅' if os.path.exists(RUFF_PATH) else '❌'}")


class RestartOnChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start()

    def start(self):
        if self.process:
            print("🔁 Redémarrage de l'application...")
            self.process.kill()

        if os.path.exists(RUFF_PATH):
            print("🧹 Nettoyage avec Ruff...")
            subprocess.run(
                [RUFF_PATH, "check", SRC_DIR, "--fix"],
                encoding="utf-8",
                errors="ignore",
            )
        else:
            print(
                "⚠️ Ruff non trouvé dans .venv\\Scripts\\. Installation automatique en cours..."
            )
            subprocess.run([sys.executable, "-m", "pip", "install", "ruff"])

            # Revérifie juste après
            if os.path.exists(RUFF_PATH):
                print("✅ Ruff installé avec succès.")
                subprocess.run(
                    [RUFF_PATH, "check", SRC_DIR, "--fix"],
                    encoding="utf-8",
                    errors="ignore",
                )
            else:
                print("❌ Échec d'installation de Ruff. Nettoyage ignoré.")

        print("🚀 Lancement de l'application...")
        self.process = subprocess.Popen([sys.executable, SCRIPT_PATH])

    def on_modified(self, event):
        if isinstance(event.src_path, str) and event.src_path.endswith(".py"):
            self.start()

    def on_created(self, event):
        if isinstance(event.src_path, str) and event.src_path.endswith(".py"):
            self.start()

    def cleanup(self):
        if self.process:
            print("🛑 Fermeture de l'application...")
            self.process.kill()


def main():
    event_handler = RestartOnChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=SRC_DIR, recursive=True)
    observer.start()

    print("👀 Surveillance des fichiers dans 'src/' (Ctrl+C pour arrêter)...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.cleanup()

    observer.join()


if __name__ == "__main__":
    main()
