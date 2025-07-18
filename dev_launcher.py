import io
import os
import subprocess
import sys
import time

SRC_PATH = os.path.abspath("src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.config.env import is_dev

# Force UTF-8 sur la sortie console si nécessaire
if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

USE_EMOJI = "TERM_PROGRAM" in os.environ or "WT_SESSION" in os.environ
SRC_DIR = "src"
SCRIPT_PATH = os.path.join(SRC_DIR, "main.py")
RUFF_PATH = os.path.join(os.path.dirname(sys.executable), "ruff.exe")


def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode())


safe_print(f"{'🔍' if USE_EMOJI else '[INFO]'} Python utilisé : {sys.executable}")
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
            self.process.wait()  # Attend que le processus soit bien terminé

        # ⚙️ Nettoyage avec Ruff si disponible
        if os.path.exists(RUFF_PATH):
            print("🧹 Nettoyage avec Ruff...")
            subprocess.run(
                [RUFF_PATH, "check", SRC_DIR, "--fix"],
                encoding="utf-8",
                errors="ignore",
            )
        else:
            print("⚠️ Ruff non trouvé. Installation...")
            subprocess.run([sys.executable, "-m", "pip", "install", "ruff"])
            if os.path.exists(RUFF_PATH):
                subprocess.run(
                    [RUFF_PATH, "check", SRC_DIR, "--fix"],
                    encoding="utf-8",
                    errors="ignore",
                )
            else:
                print("❌ Échec de l'installation de Ruff.")

        # 🚀 Lancement du script avec affichage direct dans la console
        print("🚀 Lancement de l'application...\n")
        self.process = subprocess.Popen(
            [sys.executable, SCRIPT_PATH],
            stdout=sys.stdout,  # Redirige vers la console actuelle
            stderr=sys.stderr,  # Idem pour les erreurs
        )

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
            self.process.wait()


def main():
    if not is_dev():
        # Mode production : exécution simple, pas de relance
        subprocess.run([sys.executable, SCRIPT_PATH])
        return

    # Sinon : mode dev avec surveillance automatique
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
