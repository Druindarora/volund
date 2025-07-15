# modules/parlia/services/parlia_state_manager.py


class ParliaStateManager:
    def __init__(self):
        self.max_duration = 0
        self.whisper_ready = False
        self.is_recording = False
        self.is_transcribing = False

        self._subscribers = []

    def subscribe(self, callback):
        """Permet à un composant de s'abonner aux changements d'état."""
        self._subscribers.append(callback)

    def notify(self):
        """Notifie tous les abonnés que l’état a changé."""
        for cb in self._subscribers:
            cb()

    # === Setters avec notification ===

    def set_max_duration(self, duration: int):
        self.max_duration = duration
        self.notify()

    def set_whisper_ready(self, ready: bool):
        self.whisper_ready = ready
        self.notify()

    def set_recording(self, state: bool):
        self.is_recording = state
        self.notify()

    def set_transcribing(self, state: bool):
        self.is_transcribing = state
        self.notify()

    def get_status_label(self) -> str:
        if self.is_transcribing:
            return "Statut : Transcription en cours"
        elif self.is_recording:
            return "Statut : Enregistrement en cours"
        elif self.whisper_ready and self.max_duration > 0:
            return "Statut : Prêt"
        elif not self.whisper_ready:
            return "Statut : Whisper non prêt"
        else:
            return "Statut : Incomplet"

    # === Logique de validation ===

    def is_ready_to_record(self) -> bool:
        """Indique si l'on peut lancer un enregistrement."""
        return self.whisper_ready and self.max_duration > 0 and not self.is_transcribing

    def is_ui_locked(self) -> bool:
        """Indique si l'interface doit être bloquée (ex: boutons désactivés)."""
        return self.is_recording or self.is_transcribing


parlia_state = ParliaStateManager()
