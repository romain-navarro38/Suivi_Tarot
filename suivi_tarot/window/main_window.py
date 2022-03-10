from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QWidget, QGroupBox, QPushButton, QHBoxLayout, QVBoxLayout

from window.select_joueur import SelectJoueurWindow
from window.gestion_joueur import GestionJoueurWindow


class CustomButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)

        size = QSize(100, 45)
        self.setMinimumSize(size)


# noinspection PyAttributeOutsideInit
class MainWindow(QWidget):
    """Fenêtre principal servant de hub aux différentes fonctionnalités"""
    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.gb_jouer = QGroupBox(self)
        self.btn_jouer = CustomButton("Jouer")
        self.btn_classement = CustomButton("Classement\ngénéral")
        self.btn_stat = CustomButton("Statistique")

        self.gb_gestion = QGroupBox(self)
        self.btn_joueur = CustomButton("Joueur")
        self.btn_couleur = CustomButton("Couleur")

    def modify_widgets(self):
        self.gb_jouer.setTitle("Action")
        self.gb_gestion.setTitle("Gestion")

    def create_layouts(self):
        self.main_layout = QHBoxLayout(self)
        self.jouer_layout = QVBoxLayout(self.gb_jouer)
        self.gestion_layout = QVBoxLayout(self.gb_gestion)

    def add_widgets_to_layouts(self):
        self.jouer_layout.addWidget(self.btn_jouer)
        self.jouer_layout.addWidget(self.btn_classement)
        self.jouer_layout.addWidget(self.btn_stat)
        self.main_layout.addWidget(self.gb_jouer)

        self.gestion_layout.addWidget(self.btn_joueur)
        self.gestion_layout.addWidget(self.btn_couleur)
        self.main_layout.addWidget(self.gb_gestion)

    def setup_connections(self):
        self.btn_jouer.clicked.connect(self.new_session)
        self.btn_joueur.clicked.connect(self.gestion_joueur)

    def new_session(self):
        self.session = SelectJoueurWindow()
        self.session.setWindowModality(Qt.ApplicationModal)
        self.session.show()

    def gestion_joueur(self):
        self.gestion_j = GestionJoueurWindow(self)
        # self.gestion_j.setWindowModality(Qt.ApplicationModal)
        self.gestion_j.show()
