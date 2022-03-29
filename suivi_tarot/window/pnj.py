from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QLabel, QListWidget, QPushButton, QVBoxLayout


# noinspection PyAttributeOutsideInit
class PnjWindow(QWidget):
    """Fenêtre permettant de changer le pnj tiré au hasard pour la première
    donne d'une session de 6 joueurs"""

    select_player = Signal(str)

    def __init__(self, players):
        super().__init__()

        self.players = players
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.lbl_choice = QLabel("Choix du PNJ :")
        self.lw_pnj = QListWidget()
        self.btn_select = QPushButton("Sélectionner")

    def modify_widgets(self):
        self.lw_pnj.addItems(self.players)

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_choice)
        self.main_layout.addWidget(self.lw_pnj)
        self.main_layout.addWidget(self.btn_select)

    def setup_connections(self):
        self.btn_select.clicked.connect(self.selection_pnj)
        self.lw_pnj.doubleClicked.connect(self.selection_pnj)

    def selection_pnj(self):
        """Emet vers la fenêtre parente le pseudo du pnj sélectionné"""
        if self.lw_pnj.selectedItems():
            self.select_player.emit(self.lw_pnj.currentItem().text())
            self.close()
