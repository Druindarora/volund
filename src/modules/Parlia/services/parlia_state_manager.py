# === FICHIER : parlia_state_manager.py ===
# 🔍 Audit du gestionnaire d'état global Parlia (stateless côté UI)
# --------------------------------------------------
# ✅ Structure claire et rôle bien défini : stocker l'état runtime lié à Parlia
# 📍 Reste bien dans `services/` (partagé, pas pure UI, pas core logic)
# --------------------------------------------------


from config.env import is_dev
from src.core.logger_manager import get_logger

logger = get_logger("ParliaStateManager")


class ParliaStateManager:
    def __init__(self):
        self.max_duration = 0
        self.whisper_ready = False
        self.is_recording = False
        self.is_transcribing = False

        self._subscribers = []
        self._ui_components = []

    def subscribe(self, callback):
        """Permet à un composant de s'abonner aux changements d'état."""
        self._subscribers.append(callback)

    def notify(self):
        logger.info(f"[ParliaState] Callbacks actifs : {len(self._subscribers)}")
        for cb in self._subscribers[:]:
            try:
                cb()
            except RuntimeError:
                self._subscribers.remove(cb)
            except Exception as e:
                logger.error(f"[ParliaState] Callback UI cassé : {e}")

    # === Setters avec notification ===

    def set_max_duration(self, duration: int):
        self.max_duration = duration
        self.notify()
        self._refresh_ui_state()

    def set_whisper_ready(self, ready: bool):
        self.whisper_ready = ready
        self.notify()
        self._refresh_ui_state()

    def set_recording(self, state: bool):
        self.is_recording = state
        self.notify()
        self._refresh_ui_state()

    def set_transcribing(self, state: bool):
        self.is_transcribing = state
        self.notify()
        self._refresh_ui_state()

    def get_status_info(self) -> tuple[str, str]:
        """
        Retourne un tuple (texte, status_type) où status_type ∈
        'ready', 'error', 'neutral', 'warning'
        """
        if is_dev():
            logger.debug("=== [DEBUG] get_status_info ===")
            logger.debug(f"[DEBUG] is_transcribing : {self.is_transcribing}")
            logger.debug(f"[DEBUG] is_recording    : {self.is_recording}")
            logger.debug(f"[DEBUG] whisper_ready   : {self.whisper_ready}")
            logger.debug(f"[DEBUG] max_duration    : {self.max_duration}")

        if self.is_transcribing:
            return "Transcription en cours", "warning"
        elif self.is_recording:
            return "Enregistrement en cours", "warning"
        elif self.whisper_ready and self.max_duration > 0:
            return "Prêt", "ready"
        elif not self.whisper_ready:
            return "Whisper non prêt", "error"
        else:
            return "Incomplet", "neutral"

    def cleanup_invalid_components(self):
        """
        Supprime de la liste tous les composants Qt déjà détruits.
        """
        from PySide6.QtWidgets import QWidget

        self._ui_components = [
            c
            for c in self._ui_components
            if isinstance(c, QWidget)
            and c is not None
            and not c.__dict__.get("__deleted__", False)
        ]

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

    def register_ui_component(self, panel):
        if panel not in self._ui_components:
            self._ui_components.append(panel)

    def unregister_ui_component(self, panel):
        if panel in self._ui_components:
            self._ui_components.remove(panel)

    def _refresh_ui_state(self):
        self.cleanup_invalid_components()
        for component in self._ui_components[:]:
            try:
                if hasattr(component, "apply_ui_state") and callable(
                    component.apply_ui_state
                ):
                    component.apply_ui_state()
                else:
                    logger.warning(
                        f"[ParliaState] Composant {component} ne supporte pas apply_ui_state()"
                    )
            except Exception as e:
                logger.error(f"[ParliaState] UI update échouée pour {component} : {e}")


parlia_state = ParliaStateManager()
