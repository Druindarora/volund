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
    def focus_and_code(self) -> str:
        return "Analyse tous les commentaires du fichier et code ce qui est demandé, sans modifier ce qui ne l'est pas."

    @property
    def focus_and_refacto(self) -> str:
        return (
            "Refactorise uniquement la méthode suivante pour la rendre plus claire, "
            "plus lisible ou plus efficace, sans changer son comportement."
        )


# ✅ L’instance typée
config = ParliaConfig()
