class UiStateAware:
    """
    Interface pour les panels qui supportent un état UI.
    Tous les panels héritant de cette classe doivent implémenter apply_ui_state().
    """

    def apply_ui_state(self):
        raise NotImplementedError("Le panel doit implémenter apply_ui_state()")
