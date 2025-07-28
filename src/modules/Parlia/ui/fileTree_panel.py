from PySide6.QtCore import QDir, Signal
from PySide6.QtWidgets import (
    QFileSystemModel,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


class FileTreePanel(QWidget):
    # Signal émis lorsque la sélection change
    files_selected = Signal(list)

    def __init__(self, root_path: str, parent=None):
        super().__init__(parent)

        # Configuration de l'UI
        self.setMinimumWidth(250)
        self.setWindowTitle("Explorateur de fichiers")

        # Layout principal
        layout = QVBoxLayout(self)

        # Vue de l'arborescence
        self.tree_view = QTreeView(self)

        # En-tête avec label et bouton alignés
        header_layout = QHBoxLayout()
        header = QLabel("Explorateur de fichiers", self)
        collapse_button = QPushButton("Tout refermer", self)
        collapse_button.clicked.connect(self.tree_view.collapseAll)

        header_layout.addWidget(header)
        header_layout.addStretch()  # Pousse le bouton à droite
        header_layout.addWidget(collapse_button)

        layout.addLayout(header_layout)

        # Modèle de système de fichiers
        self.model = QFileSystemModel()
        self.model.setRootPath(root_path)
        self.model.setFilter(
            QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot
        )  # Inclure dossiers et fichiers

        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(root_path))
        self.tree_view.setSelectionMode(
            QTreeView.SelectionMode.ExtendedSelection
        )  # Sélection multiple
        self.tree_view.setHeaderHidden(
            False
        )  # Afficher l'en-tête pour masquer les colonnes
        self.tree_view.setAnimated(True)  # Ouverture fluide des dossiers

        # Masquer les colonnes inutiles
        for col in range(1, self.model.columnCount()):
            self.tree_view.hideColumn(col)

        layout.addWidget(self.tree_view)

        # Connexion des signaux
        self.tree_view.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )

    def on_selection_changed(self):
        # Récupérer les fichiers sélectionnés
        selected_indexes = self.tree_view.selectionModel().selectedIndexes()
        selected_files = [
            self.model.filePath(index)
            for index in selected_indexes
            if not self.model.isDir(index)  # Ignorer les dossiers
        ]
        self.files_selected.emit(selected_files)

    def get_selected_files(self):
        # Retourner la liste des fichiers sélectionnés
        selected_indexes = self.tree_view.selectionModel().selectedIndexes()
        return [
            self.model.filePath(index)
            for index in selected_indexes
            if not self.model.isDir(index)  # Ignorer les dossiers
        ]
