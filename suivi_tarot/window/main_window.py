from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QWidget, QGroupBox, QPushButton, QHBoxLayout, QVBoxLayout

from window.select_joueur import SelectPlayerWindow
from window.gestion_joueur import ManagementPlayerWindow


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
        self.gb_play = QGroupBox(self)
        self.btn_play = CustomButton("Jouer")
        self.btn_classement = CustomButton("Classement\ngénéral")
        self.btn_statistics = CustomButton("Statistique")

        self.gb_gestion = QGroupBox(self)
        self.btn_player = CustomButton("Joueur")
        self.btn_color = CustomButton("Couleur")

    def modify_widgets(self):
        self.gb_play.setTitle("Action")
        self.gb_gestion.setTitle("Gestion")

    def create_layouts(self):
        self.main_layout = QHBoxLayout(self)
        self.play_layout = QVBoxLayout(self.gb_play)
        self.gestion_layout = QVBoxLayout(self.gb_gestion)

    def add_widgets_to_layouts(self):
        self.play_layout.addWidget(self.btn_play)
        self.play_layout.addWidget(self.btn_classement)
        self.play_layout.addWidget(self.btn_statistics)
        self.main_layout.addWidget(self.gb_play)

        self.gestion_layout.addWidget(self.btn_player)
        self.gestion_layout.addWidget(self.btn_color)
        self.main_layout.addWidget(self.gb_gestion)

    def setup_connections(self):
        self.btn_play.clicked.connect(self.new_partie)
        self.btn_player.clicked.connect(self.management_player)

    def new_partie(self):
        self.partie = SelectPlayerWindow()
        self.partie.setWindowModality(Qt.ApplicationModal)
        self.partie.show()

    def management_player(self):
        self.manage_player = ManagementPlayerWindow(self)
        # self.gestion_j.setWindowModality(Qt.ApplicationModal)
        self.manage_player.show()
