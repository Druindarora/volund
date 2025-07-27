"""
Service principal pour le module Trakia.

Ce fichier gère :
- L'enregistrement des messages envoyés
- Le nettoyage automatique des messages expirés (plus vieux que 3h)
- La récupération des messages encore valides
- Le calcul des statistiques globales (V1)

Les données sont stockées dans un fichier JSON local.
Chaque entrée contient :
- "text" : le contenu du message
- "timestamp" : la date et l'heure au format ISO (locale)
"""

from datetime import datetime, timedelta
from typing import Dict, List

from modules.trakia.services.tracker_storage import (
    FILENAME_MESSAGES,
    load_global_stats,
    load_messages,
    load_period_stats,
    load_weekday_stats,
    save_message,
    update_global_stats,
    update_period_counters,
    update_weekday_stats,
)
from src.core.user_data_manager import user_data

MESSAGE_TTL = timedelta(hours=3)


def log_message(text: str) -> None:
    timestamp = datetime.now().isoformat()
    save_message(text, timestamp)
    update_global_stats(len(text))
    update_period_counters(timestamp)
    update_weekday_stats(timestamp)
    cleanup_old_messages()


def get_all_messages() -> List[Dict]:
    messages = load_messages()
    messages.sort(key=lambda msg: msg["timestamp"])
    return messages


def get_summary() -> Dict[str, str]:
    messages = get_all_messages()
    if not messages:
        return {"active_count": "0 / 0", "expires_in": "N/A", "last_message": "N/A"}

    now = datetime.now()
    oldest_message_time = datetime.fromisoformat(messages[0]["timestamp"])
    newest_message_time = datetime.fromisoformat(messages[-1]["timestamp"])

    expires_in = str((oldest_message_time + MESSAGE_TTL - now).seconds // 60) + " min"
    last_message = str((now - newest_message_time).seconds // 60) + " min"

    return {
        "active_count": f"{len(messages)} / 80",
        "expires_in": expires_in,
        "last_message": last_message,
    }


def get_stats_summary() -> Dict[str, object]:
    global_stats = load_global_stats()
    period_stats = load_period_stats()
    weekday_stats = load_weekday_stats()

    return {
        "total_messages": global_stats["total_messages"],
        "estimated_tokens": global_stats["estimated_tokens"],
        "avg_char_per_message": global_stats["avg_char_per_message"],
        "by_period": {
            "today": period_stats["today"],
            "week": period_stats["week"],
            "month": period_stats["month"],
            "year": period_stats["year"],
        },
        "by_weekday": weekday_stats.get(datetime.now().strftime("%Y-W%U"), {}),
    }


def cleanup_old_messages() -> None:
    messages = load_messages()
    now = datetime.now()
    valid_messages = [
        msg
        for msg in messages
        if datetime.fromisoformat(msg["timestamp"]) > now - MESSAGE_TTL
    ]
    user_data.set("tracker", FILENAME_MESSAGES, [])  # 💡 Reset propre
    for msg in valid_messages:
        save_message(msg["text"], msg["timestamp"])


def estimate_total_tokens(messages: List[Dict]) -> int:
    return sum(len(msg["text"]) for msg in messages) // 4


def get_avg_chars_per_message(messages: List[Dict]) -> float:
    if not messages:
        return 0.0
    return sum(len(msg["text"]) for msg in messages) / len(messages)


def get_messages_by_period(messages: List[Dict]) -> Dict[str, int]:
    now = datetime.now()
    today = now.date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    periods = {"today": 0, "week": 0, "month": 0, "year": 0}
    for msg in messages:
        msg_time = datetime.fromisoformat(msg["timestamp"])
        if msg_time.date() == today:
            periods["today"] += 1
        if msg_time.date() >= week_start:
            periods["week"] += 1
        if msg_time.date() >= month_start:
            periods["month"] += 1
        if msg_time.date() >= year_start:
            periods["year"] += 1

    return periods


def get_messages_by_weekday(messages: List[Dict]) -> Dict[str, int]:
    weekdays = {
        "lundi": 0,
        "mardi": 0,
        "mercredi": 0,
        "jeudi": 0,
        "vendredi": 0,
        "samedi": 0,
        "dimanche": 0,
    }
    for msg in messages:
        weekday = datetime.fromisoformat(msg["timestamp"]).strftime("%A").lower()
        weekdays[weekday] += 1
    return weekdays
