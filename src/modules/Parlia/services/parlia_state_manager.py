# modules/parlia/services/parlia_state_manager.py


from config.env import is_dev


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
        print(f"[ParliaState] Callbacks actifs : {len(self._subscribers)}")
        for cb in self._subscribers[:]:
            try:
                cb()
            except RuntimeError:
                self._subscribers.remove(cb)
            except Exception as e:
                print(f"[ParliaState] Callback UI cassé : {e}")

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
        if is_dev():
            print("=== [DEBUG] get_status_label ===")
            print(f"[DEBUG] is_transcribing : {self.is_transcribing}")
            print(f"[DEBUG] is_recording    : {self.is_recording}")
            print(f"[DEBUG] whisper_ready   : {self.whisper_ready}")
            print(f"[DEBUG] max_duration    : {self.max_duration}")

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

    def unsubscribe(self, cb):
        if cb in self._subscribers:
            self._subscribers.remove(cb)


parlia_state = ParliaStateManager()
