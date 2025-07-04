import subprocess


def run_ruff():
    print("🧹 Ruff : nettoyage des imports inutiles et autres fixes...")
    subprocess.run(["ruff", "check", "src", "--fix"])
    print("✅ Ruff terminé.")


if __name__ == "__main__":
    run_ruff()
