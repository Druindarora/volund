# whisper_server.py – Serveur Whisper local pour Parlia

import os
import tempfile

# import uvicorn
import whisper
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

MODEL_NAME = "tiny"
print(f"[🔊 Whisper Server] Chargement du modèle Whisper : '{MODEL_NAME}'...")
model = whisper.load_model(MODEL_NAME)
print("[✅] Modèle chargé avec succès.\n")

app = FastAPI()


@app.post("/transcribe")
async def transcribe(audio_file: UploadFile = File(...)):
    try:
        print(f"[📥] Fichier reçu : {audio_file.filename}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            contents = await audio_file.read()
            temp_audio.write(contents)
            temp_audio_path = temp_audio.name
        print(f"[🧪] Fichier temporaire créé : {temp_audio_path}")

        result = model.transcribe(temp_audio_path)
        text = result["text"]
        print(
            f"[📝] Transcription terminée : {text[:60]}{'...' if len(text) > 60 else ''}"
        )

        os.remove(temp_audio_path)
        print(f"[🧹] Fichier temporaire supprimé.")

        return JSONResponse(content={"text": text})

    except Exception as e:
        print(f"[❌] Erreur lors de la transcription : {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    ...
