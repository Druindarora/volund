# 🧠 Whisper Server – Environnement de développement Parlia

> 🕒 Dernière mise à jour : 9 juillet 2025 à 16h30  
> ⏱️ Temps de développement estimé : 1h30

Ce microservice local permet de faire tourner Whisper en arrière-plan pendant le développement de Parlia, pour éviter de recharger le modèle à chaque fois.

---

## 🚀 Fonctionnement

- Le serveur démarre avec **FastAPI**
- Il charge **une seule fois** le modèle Whisper (**par défaut : `tiny`**)
- Il expose une route POST `/transcribe` qui accepte un fichier `.wav` et retourne le texte transcrit
- Il tourne en local : `http://127.0.0.1:5005`

---

## 📁 Structure

dev_env/
├── whisper_server.py # Serveur FastAPI (Whisper intégré)
├── start_whisper_server.bat # Script de lancement Windows
└── README.md # Ce fichier

---

## 📦 Dépendances requises

Installe-les dans ton environnement virtuel avec :

```bash
pip install fastapi uvicorn whisper python-multipart

🧪 Pour lancer le serveur
Active ton environnement virtuel Python (venv)

Lance simplement le script Windows :
start_whisper_server.bat
Celui-ci appelle le bon interpréteur Python pour démarrer le serveur.

📤 API
POST /transcribe
Champ requis (form-data) : audio_file (format .wav)

Réponse :

json
Copier
Modifier
{
  "text": "Texte dicté par l'utilisateur."
}
En cas d’erreur, la réponse contiendra un champ "error" et un code HTTP 500.

🧰 Logs console
Des logs lisibles sont affichés dans la console :

Chargement du modèle ([🔊])

Fichier reçu ([📥])

Chemin temporaire ([🧪])

Résultat de la transcription ([📝])

Nettoyage ([🧹])

Erreurs éventuelles ([❌])

🔒 Sécurité
Ce microservice n'est pas sécurisé : il ne doit être utilisé qu'en local dans un environnement de développement.