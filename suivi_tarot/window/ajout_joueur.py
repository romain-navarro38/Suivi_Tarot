from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QPushButton, QFormLayout, \
    QVBoxLayout, QHBoxLayout

from database.clients import get_joueur, ajout_joueur


# noinspection PyAttributeOutsideInit
class AjoutJoueurWindow(QWidget):

    new_pseudo = Signal(dict)
    etat_fenetre = Signal(bool)

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
        self.lbl_pseudo = QLabel("Pseudo")
        self.lbl_nom = QLabel("Nom")
        self.lbl_prenom = QLabel("Prénom")
        self.lbl_actif = QLabel("Actif")
        self.le_pseudo = QLineEdit()
        self.le_nom = QLineEdit()
        self.le_prenom = QLineEdit()
        self.chk_actif = QCheckBox("")
        self.btn_valider = QPushButton("Valider")
        self.btn_annuler = QPushButton("Annuler")

    def modify_widgets(self):
        self.le_pseudo.setPlaceholderText("5 caractères min.")
        self.le_nom.setPlaceholderText("facultatif")
        self.le_prenom.setPlaceholderText("facultatif")
        self.chk_actif.setChecked(True)

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.bouton_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.form_layout.addRow(self.lbl_pseudo, self.le_pseudo)
        self.form_layout.addRow(self.lbl_nom, self.le_nom)
        self.form_layout.addRow(self.lbl_prenom, self.le_prenom)
        self.form_layout.addRow(self.lbl_actif, self.chk_actif)
        self.bouton_layout.addWidget(self.btn_valider)
        self.bouton_layout.addWidget(self.btn_annuler)
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.bouton_layout)

    def setup_connections(self):
        self.btn_valider.clicked.connect(self.valider)
        self.btn_annuler.clicked.connect(self.close)

    def valider(self):
        joueurs = [pseudo[0] for pseudo in get_joueur()]
        if len(self.le_pseudo.text()) > 4 and \
           self.le_pseudo.text().lower() not in [joueur.lower() for joueur in joueurs]:

            actif = 1 if self.chk_actif.isChecked() else 0

            joueur_dict = {"pseudo": self.le_pseudo.text(),
                           "nom": self.le_nom.text(),
                           "prenom": self.le_prenom.text(),
                           "actif": actif}

            ajout_joueur(joueur_dict)
            self.clear_le()
            self.new_pseudo.emit(joueur_dict)

    def clear_le(self):
        self.le_pseudo.setText("")
        self.le_nom.setText("")
        self.le_prenom.setText("")
        self.chk_actif.setChecked(True)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.etat_fenetre.emit(False)
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication()
    window = AjoutJoueurWindow()
    window.show()
    app.exec()
