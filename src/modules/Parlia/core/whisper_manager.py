# 🔄 Module singleton pour gérer le modèle Whisper dans Parlia

# Ce fichier doit garantir qu’un seul modèle Whisper est chargé à la fois
# et que toutes les opérations passent par ce module centralisé.

# -----------------------------------------------------------
# 💾 Variable interne pour stocker le modèle actuel
# - initialiser à None au démarrage
# - ne jamais exposer directement en dehors de ce fichier

_current_model = None


# -----------------------------------------------------------
# 📥 Fonction : load_model(name: str)
# - Si un modèle est déjà chargé, afficher un message et ignorer
# - Sinon, charger le modèle (simulé ici) et le stocker dans _current_model
# - En dev, afficher quel modèle a été chargé


def load_model(name: str):
    global _current_model
    if _current_model is not None:
        print(f"Un modèle est déjà chargé : {_current_model}. Ignorer la demande.")
        return

    # Simuler le chargement du modèle
    _current_model = f"Modèle chargé : {name}"
    print(f"Modèle '{name}' chargé avec succès.")


# -----------------------------------------------------------
# 📤 Fonction : get_model() -> Any
# - Retourne l’objet modèle actuel
# - Peut être None si aucun modèle n’a encore été chargé


def get_model():
    return _current_model


# -----------------------------------------------------------
# ❌ Fonction : unload_model()
# - Décharge le modèle en cours (le remet à None)
# - Affiche un message de confirmation


def unload_model():
    global _current_model
    if _current_model is None:
        print("Aucun modèle n'est actuellement chargé.")
        return

    print(f"Modèle '{_current_model}' déchargé.")
    _current_model = None


# -----------------------------------------------------------
# ✅ Fonction : is_model_loaded() -> bool
# - Renvoie True si un modèle est déjà chargé, False sinon


def is_model_loaded():
    return _current_model is not None
