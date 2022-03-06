from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QLabel, QListWidget, QPushButton, QVBoxLayout


# noinspection PyAttributeOutsideInit
class PnjWindow(QWidget):

    select_joueur = Signal(str)

    def __init__(self, joueurs):
        super().__init__()

        self.joueurs = joueurs
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.lbl_choix = QLabel("Choix du PNJ :")
        self.lw_pnj = QListWidget()
        self.btn_select = QPushButton("Sélectionner")

    def modify_widgets(self):
        self.lw_pnj.addItems(self.joueurs)

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_choix)
        self.main_layout.addWidget(self.lw_pnj)
        self.main_layout.addWidget(self.btn_select)

    def setup_connections(self):
        self.btn_select.clicked.connect(self.selection_pnj)
        self.lw_pnj.doubleClicked.connect(self.selection_pnj)

    def selection_pnj(self):
        if self.lw_pnj.selectedItems():
            self.select_joueur.emit(self.lw_pnj.currentItem().text())
            self.close()
