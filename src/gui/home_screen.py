from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import QDrag, QFont, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_layout()
        self.add_static_cards()
        self.populate_modules_from_manager()
        self.enable_drag_and_drop()

    def setup_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 40, 20, 20)

        title_label = QLabel("Accueil")
        title_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        title_label.setFont(QFont("Arial", 28, QFont.Bold))
        main_layout.addWidget(title_label)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignTop)
        main_layout.addLayout(self.grid_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def create_module_card(
        self, name: str, icon_path: str, description: str, is_special: bool = False
    ) -> QFrame:
        # Crée une carte avec le nom, l'icône, la description, et optionnellement une étoile
        card = QFrame()
        card.setFixedSize(200, 200)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)

        # Étoile
        if not is_special:
            star_label = QPushButton("☆")
            star_label.setMaximumWidth(30)
            star_label.setStyleSheet("border: none;")
            layout.addWidget(star_label)
        else:
            star_label = QLabel("★")
            star_label.setAlignment(Qt.AlignLeft)
            layout.addWidget(star_label)

        # Icône
        icon_label = QLabel()
        pixmap = QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Titre
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)

        card.setLayout(layout)

        # Style commun
        card.setStyleSheet(
            "border: 1px solid #aaa; border-radius: 5px; padding: 5px; color: white;"
        )
        return card

    def add_static_cards(self):
        # Appelle la méthode générique avec des valeurs fixes
        card = self.create_module_card(
            name="Vølund",
            icon_path="assets/icons/volund.ico",
            description="Ta prochaine application...",
            is_special=True,
        )
        self.grid_layout.addWidget(card, 0, 0)

    def populate_modules_from_manager(self):
        modules = [
            {
                "name": "Module 1",
                "icon": "assets/icons/module1.ico",
                "description": "Module générique",
            },
            {
                "name": "Module 2",
                "icon": "assets/icons/module2.ico",
                "description": "Autre module",
            },
        ]

        row, col = 0, 1
        for module in modules:
            card = self.create_module_card(
                name=module["name"],
                icon_path=module["icon"],
                description=module["description"],
            )
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def enable_drag_and_drop(self):
        for i in range(self.grid_layout.count()):
            item = self.grid_layout.itemAt(i).widget()
            if i == 0:
                continue  # Ne pas dragguer la carte spéciale

            item.setAcceptDrops(True)

            def start_drag(event, widget=item):
                drag = QDrag(widget)
                mime_data = QMimeData()
                mime_data.setText(widget.objectName())
                drag.setMimeData(mime_data)
                drag.exec_()

            item.mousePressEvent = start_drag
