class ParliaSettings:
    # Transcription Panel Labels
    LABEL_RECORD: str = "Enregistrer"
    LABEL_STATUT: str = "Statut : "
    LABEL_STOP: str = "Stopper"

    LABEL_MAX_DURATION: str = "Durée max :"
    LABEL_RECORDING_TIME: str = "Temps d'enregistrement :"
    LABEL_TRANSCRIPTION_TIME: str = "Temps de transcription :"
    LABEL_TIMER_DEFAULT: str = "00:00"

    LABEL_TRANSCRIBED_TEXT: str = "Texte transcrit..."

    LABEL_NO_DURATION: str = "Aucun temps"
    LABEL_DURATION_1_MIN: str = "1 minute"
    LABEL_DURATION_2_MIN: str = "2 minutes"
    LABEL_DURATION_5_MIN: str = "5 minutes"
    LABEL_DURATION_10_MIN: str = "10 minutes"
    LABEL_DURATION_15_MIN: str = "15 minutes"

    # Action Panel Labels
    LABEL_READY: str = "Prêt"
    LABEL_CHATRELAY: str = "Copier [ChatRelay]"
    LABEL_COPY_TEXT: str = "Copier le texte"
    LABEL_ADD_FILES: str = "Ajouter des fichiers à la requête"

    LABEL_FOCUS_CHATGPT: str = "Focus ChatGPT"
    LABEL_FOCUS_VSCODE: str = "Focus VSC"
    LABEL_FOCUS_AND_CODE: str = "Focus VSC et Code"
    LABEL_FOCUS_AND_REFACTO: str = "Focus VSC et Refacto"
    LABEL_EXPLAIN_CODE: str = "Expliquer le code"
    LABEL_ANALYZE_CODE: str = "Analyser le code"

    # Settings Panel Labels
    LABEL_CURRENT_MODEL: str = "Modèle en cours : Aucun"
    LABEL_CHOOSE_FOLDER: str = "Choisir dossier"
    LABEL_INCLUDE_CONCLUSION: str = "Inclure automatiquement la phrase de conclusion"
    LABEL_CURRENT_CONCLUSION_PHRASES: str = "Phrases de conclusion actuelles :"
    LABEL_NO_CURRENT_CONCLUSION: str = "Aucun"
    LABEL_NEW_PHRASE: str = "Nouvelle phrase"
    LABEL_PLACEHOLDER_CUSTOM_PHRASE: str = (
        "Entrez votre phrase de conclusion personnalisée ici..."
    )
    LABEL_ERROR_INVALID_FOLDER: str = "Erreur : Dossier invalide."
    LABEL_NO_MODEL_SELECTED: str = "Aucun modèle sélectionné"
    LABEL_NO_MODEL_FOUND: str = "Aucun modèle trouvé dans le dossier."

    LABEL_CURRENT_MODEL: str = "Modèle en cours : {model_name}"
    LABEL_CURRENT_FOLDER: str = "Dossier sélectionné : {folder}"

    # HOME Panel Labels
    LABEL_SETTINGS_TITLE: str = "⚙️ Paramètres Whisper"
    LABEL_TRANSCRIPTION_TITLE: str = "📝 Transcription"
    LABEL_ACTIONS_TITLE: str = "🔧 Actions"
