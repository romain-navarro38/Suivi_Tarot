from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QCheckBox, QPushButton, QFormLayout, \
    QVBoxLayout, QHBoxLayout

from suivi_tarot.database.clients import insert_new_player
from suivi_tarot.api.check import player_is_valid


# noinspection PyAttributeOutsideInit
class AddPlayerWindow(QWidget):
    """Fenêtre permetant l'ajout d'un nouveau joueur.
    Seul le pseudo d'un minimum de 4 caractères est obligatoire"""

    new_nickname = Signal(dict)
    window_status = Signal(bool)

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
        self.lbl_nickname = QLabel("Pseudo")
        self.lbl_surname = QLabel("Nom")
        self.lbl_firstname = QLabel("Prénom")
        self.lbl_active = QLabel("Actif")
        self.le_nickname = QLineEdit()
        self.le_surname = QLineEdit()
        self.le_firstname = QLineEdit()
        self.chk_active = QCheckBox("")
        self.btn_validate = QPushButton("Valider")
        self.btn_cancel = QPushButton("Annuler")

    def modify_widgets(self):
        self.le_nickname.setPlaceholderText("4 caractères min.")
        self.le_surname.setPlaceholderText("facultatif")
        self.le_firstname.setPlaceholderText("facultatif")
        self.chk_active.setChecked(True)

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.button_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.form_layout.addRow(self.lbl_nickname, self.le_nickname)
        self.form_layout.addRow(self.lbl_surname, self.le_surname)
        self.form_layout.addRow(self.lbl_firstname, self.le_firstname)
        self.form_layout.addRow(self.lbl_active, self.chk_active)
        self.button_layout.addWidget(self.btn_validate)
        self.button_layout.addWidget(self.btn_cancel)
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.button_layout)

    def setup_connections(self):
        self.btn_validate.clicked.connect(self.validate)
        self.btn_cancel.clicked.connect(self.close)

    def validate(self):
        """Si pas déjà présent dans la bdd, crée un nouveau joueur dans la bdd
        et l'affiche dans la fenêtre parent"""
        if player_is_valid(self.le_nickname.text()):
            new_player = {"nickname": self.le_nickname.text(),
                          "surname": self.le_surname.text(),
                          "firstname": self.le_firstname.text(),
                          "active": self.chk_active.isChecked(),
                          "protect": False}

            insert_new_player(new_player)
            self.clear_line_edit()
            self.new_nickname.emit(new_player)

    def clear_line_edit(self):
        """Remise à zero de la fenêtre"""
        self.le_nickname.setText("")
        self.le_surname.setText("")
        self.le_firstname.setText("")
        self.chk_active.setChecked(True)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Signale à la fenêtre parent la fermeture de celle-ci"""
        self.window_status.emit(False)
        super().closeEvent(event)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    window = AddPlayerWindow()
    window.show()
    app.exec()
