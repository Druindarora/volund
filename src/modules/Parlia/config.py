# modules/parlia/config.py


class Timeouts:
    @property
    def window_switch(self) -> float:
        return 0.5

    @property
    def text_input(self) -> float:
        return 0.1

    @property
    def paste_delay(self) -> float:
        return 0.4

    @property
    def after_paste_delay(self) -> float:
        return 1.0


class ParliaConfig:
    @property
    def hotkey(self) -> str:
        return "ctrl+shift+f12"

    @property
    def focus_countdown(self) -> int:
        return 5

    @property
    def timeouts(self) -> Timeouts:
        return Timeouts()

    @property
    def vscode_window_title(self) -> str:
        return "Visual Studio Code"

    @property
    def default_countdown_message(self) -> str:
        return "Attention, vous avez {n} seconde(s) pour vous focus sur VS Code..."


# ✅ L’instance typée
config = ParliaConfig()
