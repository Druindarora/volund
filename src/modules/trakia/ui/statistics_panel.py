"""
📊 StatisticsPanel – Interface de visualisation des statistiques dans Trakia.

Ce panneau doit afficher dynamiquement les données de `tracker_service.getStatsSummary()`.

🧠 Objectif :
Remplacer toutes les valeurs statiques et données mockées (comme "1234", "50", etc.) par des valeurs réelles.

✅ Comportement attendu :
- Appeler `getStatsSummary()` du module `tracker_service` au moment de l'initialisation (`__init__`)
- Stocker le dictionnaire retourné dans une variable locale `stats`
- Mettre à jour les widgets avec les vraies valeurs issues de `stats`

📦 Détail de `stats` retourné par `getStatsSummary()` :

{
    "total_messages": int,
    "estimated_tokens": int,
    "avg_char_per_message": float,
    "by_weekday": {
        "lundi": int,
        ...
        "dimanche": int
    },
    "by_period": {
        "today": int,
        "week": int,
        "month": int,
        "year": int
    }
}

📌 Remplacements spécifiques à faire :
- Section 1 – Indicateurs globaux :
    - Remplacer "1234" par `stats["total_messages"]`
    - Remplacer "56789" par `stats["estimated_tokens"]`
    - Remplacer "45" par `stats["avg_char_per_message"]`

- Section 2 – Répartition par jour :
    - Générer dynamiquement les lignes à partir de `stats["by_weekday"]`
    - Trier les jours selon l'ordre standard : lundi → dimanche

- Section 3 – Périodes :
    - Remplacer les valeurs par `stats["by_period"]["today"]`, etc.

🧹 Supprimer tout ce qui est hardcodé ou temporaire.
"""

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ..services.tracker_service import get_stats_summary


class StatisticsPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Récupérer les statistiques réelles
        stats = get_stats_summary()
        if not isinstance(stats, dict):
            stats = {
                "total_messages": 0,
                "estimated_tokens": 0,
                "avg_char_per_message": 0.0,
                "by_weekday": {
                    "lundi": 0,
                    "mardi": 0,
                    "mercredi": 0,
                    "jeudi": 0,
                    "vendredi": 0,
                    "samedi": 0,
                    "dimanche": 0,
                },
                "by_period": {"today": 0, "week": 0, "month": 0, "year": 0},
            }

        by_weekday = (
            stats["by_weekday"] if isinstance(stats["by_weekday"], dict) else {}
        )
        by_period = stats["by_period"] if isinstance(stats["by_period"], dict) else {}

        # Partie 1 – Indicateurs globaux
        global_indicators_layout = QHBoxLayout()
        global_indicators_layout.addWidget(
            self.create_stat_card("Messages envoyés", str(stats["total_messages"]))
        )
        global_indicators_layout.addWidget(
            self.create_stat_card("Tokens générés", str(stats["estimated_tokens"]))
        )
        global_indicators_layout.addWidget(
            self.create_stat_card(
                "Moyenne caractères", f"{stats['avg_char_per_message']:.2f}"
            )
        )
        layout.addLayout(global_indicators_layout)

        # Partie 2 – Répartition par jour de la semaine
        days_layout = QVBoxLayout()
        days_order = [
            "lundi",
            "mardi",
            "mercredi",
            "jeudi",
            "vendredi",
            "samedi",
            "dimanche",
        ]
        for day in days_order:
            count = by_weekday.get(day, 0)
            day_label = QLabel(f"{day.capitalize()}: {count} messages")
            day_label.setStyleSheet("padding: 5px; color: white;")
            days_layout.addWidget(day_label)
        layout.addLayout(days_layout)

        # Partie 3 – Messages par période
        periods_layout = QGridLayout()
        periods = [
            ("Aujourd'hui", by_period.get("today", 0)),
            ("Semaine", by_period.get("week", 0)),
            ("Mois", by_period.get("month", 0)),
            ("Année", by_period.get("year", 0)),
        ]
        for i, (period, count) in enumerate(periods):
            period_card = self.create_stat_card(period, str(count))
            periods_layout.addWidget(period_card, i // 2, i % 2)
        layout.addLayout(periods_layout)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #2b2b2b; color: white;")

    def create_stat_card(self, title, value):
        card = QFrame()
        card.setStyleSheet(
            "background-color: #3c3c3c; border-radius: 8px; padding: 10px; margin: 5px;"
        )
        card_layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 18px;")
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        card.setLayout(card_layout)
        return card
