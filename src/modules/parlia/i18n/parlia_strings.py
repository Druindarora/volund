# === FICHIER : settings.py (racine module parlia) ===
# 🔍 Audit du fichier de constantes de texte (libellés UI)
# --------------------------------------------------
# ✅ Rôle : centralise les libellés visibles dans l’interface utilisateur de Parlia
# --------------------------------------------------

# ✅ Points positifs :
# - Organisation claire par sections (Transcription, Action, Settings, Home)
# - Facilite les futures traductions ou modifications globales
# - Utilisation en mode `ParliaSettings.LABEL_XXX` = lisible et robuste

# 🛠 Suggestions d’amélioration :
# 4. 📦 Charger depuis un fichier JSON/YAML si passage à la localisation multi-langues

# ✅ Conclusion :
# Garde-le tel quel pour l’instant, mais il est un bon candidat à évoluer vers une **infrastructure i18n** plus formelle


class ParliaStrings:
    class Transcription:
        RECORD = "Enregistrer"
        STATUT = "Statut : "
        STOP = "Stopper"
        MAX_DURATION = "Durée max :"
        RECORDING_TIME = "Temps d'enregistrement :"
        TRANSCRIPTION_TIME = "Temps de transcription :"
        TIMER_DEFAULT = "00:00"
        TRANSCRIBED_TEXT = "Texte transcrit..."
        NO_DURATION = "Aucun temps"
        DURATION_1_MIN = "1 minute"
        DURATION_2_MIN = "2 minutes"
        DURATION_5_MIN = "5 minutes"
        DURATION_10_MIN = "10 minutes"
        DURATION_15_MIN = "15 minutes"

    class Action:
        READY = "Prêt"
        CHATRELAY = "Copier [ChatRelay]"
        COPY_TEXT = "Copier le texte"
        ADD_FILES = "Ajouter des fichiers à la requête"
        FOCUS_CHATGPT = "Focus ChatGPT"
        FOCUS_VSCODE = "Focus VSC"
        FOCUS_AND_CODE = "Focus VSC et Code"
        FOCUS_AND_REFACTO = "Focus VSC et Refacto"
        EXPLAIN_CODE = "Expliquer le code"
        ANALYZE_CODE = "Analyser le code"

    class Settings:
        CURRENT_MODEL = "Modèle en cours : Aucun"
        CHOOSE_FOLDER = "Choisir dossier"
        INCLUDE_CONCLUSION = (
            "Inclure automatiquement la phrase de conclusion (non codé)"
        )
        CURRENT_CONCLUSION_PHRASES = "Phrases de conclusion actuelles :"
        NO_CURRENT_CONCLUSION = "Aucun"
        NEW_PHRASE = "Nouvelle phrase"
        PLACEHOLDER_CUSTOM_PHRASE = (
            "Entrez votre phrase de conclusion personnalisée ici..."
        )
        ERROR_INVALID_FOLDER = "Erreur : Dossier invalide."
        NO_MODEL_SELECTED = "Aucun modèle sélectionné"
        NO_MODEL_FOUND = "Aucun modèle trouvé dans le dossier."
        CURRENT_FOLDER = "Dossier sélectionné : {folder}"

    class Home:
        SETTINGS_TITLE = "⚙️ Paramètres"
        TRANSCRIPTION_TITLE = "📝 Transcription"
        ACTIONS_TITLE = "🔧 Actions"

    @staticmethod
    def as_dict():
        return {
            "TRANSCRIPTION": {
                attr: getattr(ParliaStrings.Transcription, attr)
                for attr in dir(ParliaStrings.Transcription)
                if not attr.startswith("_")
            },
            "ACTION": {
                attr: getattr(ParliaStrings.Action, attr)
                for attr in dir(ParliaStrings.Action)
                if not attr.startswith("_")
            },
            "SETTINGS": {
                attr: getattr(ParliaStrings.Settings, attr)
                for attr in dir(ParliaStrings.Settings)
                if not attr.startswith("_")
            },
            "HOME": {
                attr: getattr(ParliaStrings.Home, attr)
                for attr in dir(ParliaStrings.Home)
                if not attr.startswith("_")
            },
        }
