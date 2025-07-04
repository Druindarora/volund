import os
import subprocess
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

SCRIPT_PATH = os.path.join("src", "main.py")
SRC_DIR = "src"


class RestartOnChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start()

    def start(self):
        if self.process:
            print("🔁 Redémarrage de l'application...")

            # Arrêt de l'ancienne instance
            self.process.kill()

        print("🧹 Nettoyage avec Ruff...")
        subprocess.run(["ruff", "check", SRC_DIR, "--fix"])

        print("🚀 Lancement de l'application...")
        self.process = subprocess.Popen([sys.executable, SCRIPT_PATH])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            self.start()

    def on_created(self, event):
        if event.src_path.endswith(".py"):
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
