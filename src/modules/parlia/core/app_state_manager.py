from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Optional

from PySide6.QtCore import QElapsedTimer, QObject, QTimer, Signal

# --- Énumérations d'état et services ---


class TranscriptionState(Enum):
    """Cycle d'état de la transcription côté client."""

    IDLE = "idle"  # prêt à enregistrer
    RECORDING = "recording"  # micro en cours
    PROCESSING = "processing"  # envoi/transcription serveur
    READY = "ready"  # transcription disponible
    ERROR = "error"  # échec (mais UI déverrouillée)


class ServiceKind(Enum):
    """Services gérés centralement (extensible)."""

    WHISPER = "whisper"
    OLLAMA = "ollama"


# --- Modèle d'état d'un service ---


@dataclass
class ServiceStatus:
    """Statut d'un service tel que connu côté client."""

    available: bool = False  # dispo côté serveur (bool)
    state: str = "unknown"  # ex. "loading" | "ready" | "error" | "unknown"
    model: Optional[str] = None  # modèle actif si pertinent

    @property
    def ready(self) -> bool:
        """Prêt à être utilisé au sens métier (ex. available && state == 'ready')."""
        return bool(self.available and self.state == "ready")

    def toDict(self) -> Dict[str, Any]:
        """Version dict sérialisable (inclut la clé 'ready')."""
        data = asdict(self)
        data["ready"] = self.ready
        return data


# --- Gestionnaire d'état global (singleton QObject) ---


class AppStateManager(QObject):
    """
    Gestionnaire d'état global de l'application (singleton).
    - Centralise le cycle de transcription (idle/recording/processing/ready/error).
    - Centralise la disponibilité des services (whisper/ollama/…).
    - Émet des signaux pour que l'UI et les services se synchronisent sans duplication de logique.

    ⚙️ Conventions:
      - Identifiants/méthodes en anglais.
      - Commentaires explicatifs en français.
      - Méthodes en camelCase (spécification du projet).
    """

    # --- Signaux globaux ---

    # État de transcription modifié (valeur str de TranscriptionState).
    stateChanged = Signal(str)

    # Un service a changé (nom du service, snapshot dict).
    serviceStatusChanged = Signal(str, dict)

    # Tous les services (snapshot dict {serviceName: statusDict}).
    servicesUpdated = Signal(dict)

    # Capacités opérationnelles (ex. {"canRecord": bool, "canUseActions": bool, "busy": bool}).
    capabilitiesUpdated = Signal(dict)

    # Busy = True quand RECORDING ou PROCESSING (pratique pour (dés)activer l'UI de façon large).
    busyChanged = Signal(bool)

    # Ticks des timers (en secondes flottantes).
    recordingTimerTick = Signal(float)
    processingTimerTick = Signal(float)

    # Resets explicites des timers (pour forcer l'UI à remettre 00:00 / 00:00.00).
    recordingTimerReset = Signal()
    processingTimerReset = Signal()

    # Action refusée (ex. startRecording alors que whisper non prêt).
    actionRejected = Signal(str, str)  # (reasonCode, humanMessage)

    # --- Singleton ---

    _instance: Optional["AppStateManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "AppStateManager":
        # Retourne toujours la même instance
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Protection contre double initialisation de QObject (PySide6)
        if AppStateManager._initialized:
            return
        super().__init__()
        AppStateManager._initialized = True

        # --- Initialisation réelle ---

        # État de transcription courant
        self._state: TranscriptionState = TranscriptionState.IDLE

        # Statuts des services (extensible)
        self._services: Dict[str, ServiceStatus] = {
            ServiceKind.WHISPER.value: ServiceStatus(),
            ServiceKind.OLLAMA.value: ServiceStatus(),
        }

        # Cache des capacités calculées (pour n'émettre que sur changement)
        self._capabilities: Dict[str, bool] = {
            "canRecord": False,
            "canUseActions": False,
            "busy": False,
        }

        # Timers (enregistrement = 1s, processing = 100ms)
        self._recordingElapsed = QElapsedTimer()
        self._recordingTicker = QTimer(self)
        self._recordingTicker.setInterval(1000)
        self._recordingTicker.timeout.connect(self._onRecordingTick)

        self._processingElapsed = QElapsedTimer()
        self._processingTicker = QTimer(self)
        self._processingTicker.setInterval(100)  # centièmes (~0.1s)
        self._processingTicker.timeout.connect(self._onProcessingTick)

        # Calcul initial des capacités
        self._recomputeCapabilities(emitAlways=True)

    # --- Accesseurs d'état ---

    def currentState(self) -> TranscriptionState:
        """Retourne l'état de transcription courant."""
        return self._state

    def services(self) -> Dict[str, ServiceStatus]:
        """Retourne une copie superficielle des services (objet mutable à ne pas modifier directement)."""
        return dict(self._services)

    # --- Helpers "ready" rapides ---

    def isWhisperReady(self) -> bool:
        """Convenience: état boolean 'WHISPER prêt'."""
        return self._services[ServiceKind.WHISPER.value].ready

    def isOllamaReady(self) -> bool:
        """Convenience: état boolean 'OLLAMA prêt'."""
        return self._services[ServiceKind.OLLAMA.value].ready

    # --- Gestion du cycle de transcription (API haute-niveau, gatekeepers inclus) ---

    def requestStartRecording(self) -> bool:
        """
        Demande à démarrer l'enregistrement.
        Refuse si Whisper n'est pas prêt ou si on n'est pas IDLE/READY/ERROR.
        """
        if not self.isWhisperReady():
            self.actionRejected.emit("whisper_not_ready", "Whisper n'est pas prêt.")
            return False
        if self._state not in (
            TranscriptionState.IDLE,
            TranscriptionState.READY,
            TranscriptionState.ERROR,
        ):
            self.actionRejected.emit(
                "invalid_state", f"Impossible de démarrer depuis l'état {self._state.value}."
            )
            return False

        self._enterRecording()
        return True

    def requestStopRecordingAndProcess(self) -> bool:
        """
        Demande à arrêter l'enregistrement et à passer en traitement (upload + transcription).
        Refuse si on n'est pas en RECORDING.
        """
        if self._state != TranscriptionState.RECORDING:
            self.actionRejected.emit(
                "invalid_state", "Stop/Process seulement en cours d'enregistrement."
            )
            return False

        self._enterProcessing()
        return True

    def markTranscriptionReady(self) -> None:
        """À appeler quand le texte est disponible (réponse serveur reçue côté client)."""
        self._enterReady()

    def markTranscriptionError(self, message: str = "Erreur de transcription.") -> None:
        """À appeler en cas d'erreur (réseau, serveur, format, etc.)."""
        self._enterError(message)

    def resetToIdle(self) -> None:
        """Réinitialise le cycle (ex: après affichage, on repart à zéro)."""
        self._setState(TranscriptionState.IDLE)
        # On ne reset pas forcément les services; uniquement le cycle.
        self._resetRecordingTimer()
        self._resetProcessingTimer()

    # --- Mises à jour de services (depuis StatusEventHub ou autres) ---

    def updateService(
        self, name: str | ServiceKind, status: ServiceStatus | Dict[str, Any]
    ) -> None:
        """
        Met à jour un service et émet les signaux appropriés.
        - name: "whisper" | "ollama" | ...
        - status: ServiceStatus ou dict compatible {available, state, model}
        """
        serviceName = name.value if isinstance(name, ServiceKind) else str(name)
        if serviceName not in self._services:
            # Service inconnu → on l'enregistre dynamiquement (extensibilité)
            self._services[serviceName] = ServiceStatus()

        old = self._services[serviceName]
        new = (
            status
            if isinstance(status, ServiceStatus)
            else ServiceStatus(
                available=bool(status.get("available", old.available)),
                state=str(status.get("state", old.state)),
                model=status.get("model", old.model),
            )
        )
        changed = (
            (old.available != new.available) or (old.state != new.state) or (old.model != new.model)
        )

        if changed:
            self._services[serviceName] = new
            self.serviceStatusChanged.emit(serviceName, new.toDict())
            self.servicesUpdated.emit({k: v.toDict() for k, v in self._services.items()})
            self._recomputeCapabilities()

    def applyServerSnapshot(self, snapshot: Dict[str, Any]) -> None:
        """
        Applique un snapshot complet reçu du serveur (format souple).
        Exemple attendu (mais on reste tolérant) :
        {
          "whisper": {"available": true, "state": "ready", "model": "base"},
          "ollama":  {"available": true, "state": "ready", "model": "qwen2.5"}
        }
        """
        changed = False
        for key in (ServiceKind.WHISPER.value, ServiceKind.OLLAMA.value):
            if key in snapshot and isinstance(snapshot[key], dict):
                before = self._services.get(key, ServiceStatus())
                data = snapshot[key]
                after = ServiceStatus(
                    available=bool(data.get("available", before.available)),
                    state=str(data.get("state", before.state)),
                    model=data.get("model", before.model),
                )
                if (before.available, before.state, before.model) != (
                    after.available,
                    after.state,
                    after.model,
                ):
                    self._services[key] = after
                    self.serviceStatusChanged.emit(key, after.toDict())
                    changed = True

        if changed:
            self.servicesUpdated.emit({k: v.toDict() for k, v in self._services.items()})
            self._recomputeCapabilities()

    # --- Calcul des capacités globales (gates UI) ---

    def _recomputeCapabilities(self, emitAlways: bool = False) -> None:
        """
        Calcule les capacités opérationnelles:
          - canRecord: Whisper prêt ET pas d'opération en cours.
          - canUseActions: Ollama prêt ET pas d'opération en cours.
          - busy: enregistrement ou traitement en cours.
        """
        busy = self._state in (TranscriptionState.RECORDING, TranscriptionState.PROCESSING)
        canRecord = self.isWhisperReady() and not busy
        canUseActions = self.isOllamaReady() and not busy

        newCaps = {"canRecord": canRecord, "canUseActions": canUseActions, "busy": busy}

        if emitAlways or newCaps != self._capabilities:
            self._capabilities = newCaps
            self.capabilitiesUpdated.emit(dict(self._capabilities))
            self.busyChanged.emit(busy)

    # --- Transitions internes d'état (timer + signaux) ---

    def _setState(self, newState: TranscriptionState) -> None:
        if newState != self._state:
            self._state = newState
            self.stateChanged.emit(newState.value)
            self._recomputeCapabilities()

    def _enterRecording(self) -> None:
        # Reset processing timer au cas où
        self._resetProcessingTimer()

        # Démarre l'enregistrement
        self._setState(TranscriptionState.RECORDING)
        self._startRecordingTimer()

    def _enterProcessing(self) -> None:
        # Stoppe l'enregistrement, démarre le processing
        self._stopRecordingTimer()
        self._setState(TranscriptionState.PROCESSING)
        self._startProcessingTimer()

    def _enterReady(self) -> None:
        # Fin de traitement OK
        self._stopProcessingTimer()
        self._setState(TranscriptionState.READY)

    def _enterError(self, message: str) -> None:
        # Fin de traitement KO
        self._stopProcessingTimer()
        self._setState(TranscriptionState.ERROR)
        self.actionRejected.emit("processing_error", message)

    # --- Timers: enregistrement ---

    def _startRecordingTimer(self) -> None:
        """Démarre le timer d'enregistrement et émet un reset d'affichage."""
        self._recordingElapsed.start()
        self.recordingTimerReset.emit()
        self._recordingTicker.start()
        # Premier tick immédiat (0.0s) pour synchro UI
        self.recordingTimerTick.emit(0.0)

    def _stopRecordingTimer(self) -> None:
        """Stoppe le timer d'enregistrement (dernier tick émis)."""
        if self._recordingTicker.isActive():
            self._recordingTicker.stop()
            secs = self._elapsedSeconds(self._recordingElapsed)
            self.recordingTimerTick.emit(secs)

    def _resetRecordingTimer(self) -> None:
        """Réinitialise visuellement (00:00)."""
        if self._recordingTicker.isActive():
            self._recordingTicker.stop()
        self.recordingTimerReset.emit()

    def _onRecordingTick(self) -> None:
        secs = self._elapsedSeconds(self._recordingElapsed)
        self.recordingTimerTick.emit(secs)

    # --- Timers: processing (upload + transcription + latence retour) ---

    def _startProcessingTimer(self) -> None:
        """Démarre le timer de traitement complet (du Stop → texte reçu)."""
        self._processingElapsed.start()
        self.processingTimerReset.emit()
        self._processingTicker.start()
        self.processingTimerTick.emit(0.0)

    def _stopProcessingTimer(self) -> None:
        """Stoppe le timer de traitement (dernier tick émis)."""
        if self._processingTicker.isActive():
            self._processingTicker.stop()
            secs = self._elapsedSeconds(self._processingElapsed)
            self.processingTimerTick.emit(secs)

    def _resetProcessingTimer(self) -> None:
        """Réinitialise visuellement (00:00.00)."""
        if self._processingTicker.isActive():
            self._processingTicker.stop()
        self.processingTimerReset.emit()

    def _onProcessingTick(self) -> None:
        secs = self._elapsedSeconds(self._processingElapsed)
        self.processingTimerTick.emit(secs)

    # --- Utilitaires ---

    @staticmethod
    def _elapsedSeconds(timer: QElapsedTimer) -> float:
        """Renvoie le temps écoulé en secondes (float) à partir d'un QElapsedTimer."""
        # .isValid() n'existe pas sur toutes versions; on tolère 0 si pas démarré.
        try:
            msecs = timer.elapsed()
        except Exception:
            msecs = 0
        return max(0.0, float(msecs) / 1000.0)
