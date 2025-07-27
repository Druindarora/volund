# tracker_storage.py

"""
Utilisation de UserDataManager (déjà importé sous le nom `user_data`)

Structure du fichier JSON associé au module "tracker" :

- "trakia_messages" : liste des messages actifs (moins de 3h)
- "trakia_stat_global" : stats globales (total, tokens, moyenne)
- "trakia_stat_period" : stats today / week / month / year
- "trakia_stat_weekly" : stats par jour de la semaine

Exemples d'appel :
- user_data.get("tracker", "trakia_messages") → Liste des messages
- user_data.set("tracker", "trakia_messages", nouvelle_liste)
"""

"""
📦 TrackerStorage – Gestion des fichiers de données persistantes pour le module Trakia.

Ce module regroupe toutes les fonctions de lecture et d’écriture vers les fichiers JSON suivants :
- `trakia_messages.json` → messages envoyés récents (≤ 3h)
- `trakia_stats_global.json` → statistiques cumulées (total, tokens estimés, moyenne)
- `trakia_stats_weekly.json` → répartition par jour de la semaine (lundi → dimanche)
- `trakia_stats_period.json` → stats par période (today, week, month, year)

⚠️ Tous les fichiers sont stockés automatiquement dans le dossier `user_data/` via `UserDataManager`.

➡️ **À chaque accès** :
- Si le fichier n’existe pas → il est créé avec des valeurs par défaut.
- Si une clé attendue est absente → elle est ajoutée avec sa valeur de départ.

🎯 Objectif : Assurer un fonctionnement sans crash ni configuration manuelle, même au premier lancement.
"""

"""
À chaque lecture ou écriture :
- Si le fichier n'existe pas, il doit être créé.
- Si une clé est manquante dans un dictionnaire, elle doit être ajoutée à 0 ou à une valeur par défaut.
On utilise le `UserDataManager` pour accéder aux fichiers JSON dans le dossier user_data/.



Copilot, chaque fonction doit vérifier que la structure chargée contient bien les clés nécessaires. Si elles sont absentes, initialise-les avec une valeur par défaut avant de continuer. Utilise user_data.get("tracker", key) et user_data.set("tracker", key, value) pour interagir avec les fichiers.



"""

from datetime import datetime, timedelta
from typing import Dict, List

from src.core.user_data_manager import user_data

PREFIX = "trakia"
FILENAME_MESSAGES = f"{PREFIX}_messages.json"
FILENAME_STATS_GLOBAL = f"{PREFIX}_stat_global.json"
FILENAME_STATS_PERIOD = f"{PREFIX}_stat_period.json"
FILENAME_STATS_WEEKLY = f"{PREFIX}_stat_weekly.json"


# À insérer dans tous les modules appelants :
# Exemple : user_data.set("tracker", FILENAME_MESSAGES, [...])

# Utilisation :
# - get("tracker", FILENAME_X) → lecture
# - set("tracker", FILENAME_X, valeur) → écriture
# Ces appels créeront automatiquement le fichier si besoin.
# L'initialisation des objets doit être gérée dans chaque fonction de ce fichier.


def save_message(text: str, timestamp: str) -> None:
    """
    Sauvegarde un message dans `trakia_messages.json` en ajoutant :
    - "text" : le contenu du message
    - "timestamp" : l'horodatage ISO du moment de l'envoi

    Cette fonction :
    - Charge les messages existants
    - Ajoute le nouveau message
    - Supprime ceux plus vieux que 3h
    - Sauvegarde le résultat à nouveau

    Args:
        text (str): contenu du message
        timestamp (str): timestamp ISO 8601 (ex : "2025-07-28T19:03:42")
    """
    if not text or not timestamp:
        return  # 💡 Ignore les messages vides

    messages = user_data.get("tracker", FILENAME_MESSAGES)
    if not isinstance(messages, list):
        messages = []
    cutoff_time = datetime.fromisoformat(timestamp) - timedelta(hours=3)
    messages = [
        msg
        for msg in messages
        if datetime.fromisoformat(msg.get("timestamp", "")) > cutoff_time
    ]
    messages.append({"text": text, "timestamp": timestamp})
    user_data.set("tracker", FILENAME_MESSAGES, messages)


def update_global_stats(nb_chars: int) -> None:
    """
    Met à jour `trakia_stat_global.json` :

    - Incrémente le compteur total de messages
    - Met à jour la somme totale des caractères envoyés
    - Recalcule la moyenne automatiquement
    - Estime le nombre de tokens (caractères // 4)

    Args:
        nb_chars (int): longueur du message envoyé
    """
    stats = user_data.get("tracker", FILENAME_STATS_GLOBAL)
    if not isinstance(stats, dict):
        stats = {
            "total_messages": 0,
            "total_chars": 0,
            "estimated_tokens": 0,
            "avg_char_per_message": 0,
        }
    stats["total_messages"] += 1
    stats["total_chars"] += nb_chars
    stats["estimated_tokens"] = stats["total_chars"] // 4
    stats["avg_char_per_message"] = stats["total_chars"] // stats["total_messages"]
    user_data.set("tracker", FILENAME_STATS_GLOBAL, stats)


def update_period_counters(timestamp: str) -> None:
    """
    Met à jour `trakia_stat_period.json` avec :
    - today (+1)
    - week (+1)
    - month (+1)
    - year (+1)

    Si la date a changé depuis la dernière exécution :
    - Reset du champ "today"
    - Ajoute l'ancien "today" dans les autres compteurs

    Args:
        timestamp (str): timestamp ISO du message
    """
    stats = user_data.get("tracker", FILENAME_STATS_PERIOD)
    if not isinstance(stats, dict):
        stats = {"today": 0, "week": 0, "month": 0, "year": 0, "last_date": ""}
    current_date = datetime.fromisoformat(timestamp).date()
    last_date = stats.get("last_date", "")
    if last_date and datetime.fromisoformat(last_date).date() != current_date:
        stats["week"] += stats["today"]
        stats["month"] += stats["today"]
        stats["year"] += stats["today"]
        stats["today"] = 0
    stats["today"] += 1
    stats["last_date"] = timestamp
    user_data.set("tracker", FILENAME_STATS_PERIOD, stats)


def update_weekday_stats(timestamp: str) -> None:
    """
    Met à jour `trakia_stat_weekly.json` :
    - Identifie la semaine actuelle (`YYYY-WW`)
    - Incrémente le jour correspondant (lundi à dimanche)

    Cette méthode conserve un historique hebdomadaire lisible.

    Args:
        timestamp (str): timestamp ISO du message
    """
    stats = user_data.get("tracker", FILENAME_STATS_WEEKLY)
    if not isinstance(stats, dict):
        stats = {}
    current_week = datetime.fromisoformat(timestamp).strftime("%Y-W%U")
    if current_week not in stats:
        stats[current_week] = {
            "lundi": 0,
            "mardi": 0,
            "mercredi": 0,
            "jeudi": 0,
            "vendredi": 0,
            "samedi": 0,
            "dimanche": 0,
        }
        weekday_map = {
            "monday": "lundi",
            "tuesday": "mardi",
            "wednesday": "mercredi",
            "thursday": "jeudi",
            "friday": "vendredi",
            "saturday": "samedi",
            "sunday": "dimanche",
        }
        weekday_en = datetime.fromisoformat(timestamp).strftime("%A").lower()
        weekday = weekday_map.get(weekday_en)
        if weekday:
            stats[current_week][weekday] += 1

    stats[current_week][weekday] += 1
    user_data.set("tracker", FILENAME_STATS_WEEKLY, stats)


def load_messages() -> List[Dict]:
    """
    Charge tous les messages actifs depuis `trakia_messages.json`
    (les messages expirés doivent déjà avoir été nettoyés au moment du save).

    Returns:
        list of dict: liste de messages {"text", "timestamp"}
    """
    messages = user_data.get("tracker", FILENAME_MESSAGES)
    return messages if isinstance(messages, list) else []


def load_global_stats() -> Dict[str, object]:
    """
    Charge les statistiques globales depuis `trakia_stat_global.json` :
    - total_messages
    - total_chars
    - estimated_tokens
    - avg_char_per_message

    Returns:
        dict
    """
    stats = user_data.get("tracker", FILENAME_STATS_GLOBAL)
    return (
        stats
        if isinstance(stats, dict)
        else {
            "total_messages": 0,
            "total_chars": 0,
            "estimated_tokens": 0,
            "avg_char_per_message": 0,
        }
    )


def load_period_stats() -> Dict[str, int]:
    """
    Charge les compteurs par période depuis `trakia_stat_period.json` :
    - today
    - week
    - month
    - year

    Returns:
        dict
    """
    stats = user_data.get("tracker", FILENAME_STATS_PERIOD)
    if not isinstance(stats, dict):
        stats = {"today": 0, "week": 0, "month": 0, "year": 0, "last_date": ""}
    # Exclure la clé 'last_date' pour correspondre au type attendu
    return {key: stats[key] for key in ["today", "week", "month", "year"]}


def load_weekday_stats() -> Dict[str, Dict[str, int]]:
    """
    Charge l’historique hebdomadaire depuis `trakia_stat_weekly.json`.

    Format :
    {
        "2025-W30": {
            "lundi": 12,
            "mardi": 9,
            ...
        }
    }

    Returns:
        dict
    """
    stats = user_data.get("tracker", FILENAME_STATS_WEEKLY)
    return stats if isinstance(stats, dict) else {}
