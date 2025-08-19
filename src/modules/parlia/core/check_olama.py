import subprocess


def checkWslInstalled() -> bool:
    """
    Vérifie si WSL est installé sur la machine Windows.
    """
    try:
        subprocess.run(
            ["wsl.exe", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except FileNotFoundError:
        print("WSL n'est pas installé sur cette machine.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la vérification de WSL : {e}")
    return False


def isOllamaRunning() -> bool:
    """
    Vérifie si le service OLLAMA est en cours d'exécution dans WSL.
    """
    try:
        result = subprocess.run(
            ["wsl.exe", "ps", "-C", "ollama"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "ollama" in result.stdout:
            return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la vérification du service OLLAMA : {e}")
    return False


def startOllamaService() -> bool:
    """
    Démarre le service OLLAMA dans WSL.
    """
    try:
        subprocess.run(
            ["wsl.exe", "ollama", "serve"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("Service OLAMA démarré avec succès.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du démarrage du service OLAMA : {e}")
    return False


def main():
    """
    Orchestration de la vérification et du démarrage du service OLAMA.
    """
    if not checkWslInstalled():
        print("WSL n'est pas disponible. Veuillez l'installer pour continuer.")
        return

    if isOllamaRunning():
        print("Le service OLLAMA est déjà en cours d'exécution.")
    else:
        print("Le service OLLAMA n'est pas actif. Tentative de démarrage...")
        if startOllamaService():
            print("Le service OLLAMA a été démarré avec succès.")
        else:
            print("Échec du démarrage du service OLLAMA.")


if __name__ == "__main__":
    main()
