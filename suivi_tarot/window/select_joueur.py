from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QAbstractItemView, \
    QListWidgetItem

from database.clients import get_joueur_actif
from window.table import TableWindow


# noinspection PyAttributeOutsideInit
class SelectJoueurWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.selected = set()
        self.ordre = {}
        self.resize(176, 344)
        self.setWindowTitle("Sélection des joueurs")
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.lbl_liste = QLabel("Joueurs autour de la table :")
        self.lw_joueur = QListWidget()
        self.lbl_nb_joueur = QLabel("0 sélectionné")
        self.btn_valider = QPushButton("Valider")
        self.btn_annuler = QPushButton("Annuler")

    def modify_widgets(self):
        self.btn_valider.setEnabled(False)
        liste_joueur = [QListWidgetItem(j[0]).text() for j in get_joueur_actif()]
        self.lw_joueur.addItems(liste_joueur)
        self.lw_joueur.setSelectionMode(QAbstractItemView.MultiSelection)

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.bouton_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_liste)
        self.main_layout.addWidget(self.lw_joueur)
        self.main_layout.addWidget(self.lbl_nb_joueur)
        self.bouton_layout.addWidget(self.btn_valider)
        self.bouton_layout.addWidget(self.btn_annuler)
        self.main_layout.addLayout(self.bouton_layout)

    def setup_connections(self):
        self.lw_joueur.itemSelectionChanged.connect(self.select_valid)
        self.btn_valider.clicked.connect(self.lancement_session)
        self.btn_annuler.clicked.connect(self.close)

    def select_valid(self):
        liste = {elem.text() for elem in self.lw_joueur.selectedItems()}
        if liste - self.selected:
            pseudo = (liste - self.selected).pop()
            self.selected.add(pseudo)
            self.ordre[pseudo] = len(self.selected)
        else:
            pseudo = (self.selected - liste).pop()
            self.selected.remove(pseudo)
            rang = self.ordre[pseudo]
            del self.ordre[pseudo]
            for cle in self.ordre:
                if self.ordre[cle] > rang:
                    self.ordre[cle] -= 1

        nb_select = len(self.selected)
        if nb_select > 1:
            self.lbl_nb_joueur.setText(f"{nb_select} sélectionnés")
        else:
            self.lbl_nb_joueur.setText(f"{nb_select} sélectionné")

        if 2 < nb_select < 7:
            self.btn_valider.setEnabled(True)
        else:
            self.btn_valider.setEnabled(False)

    def lancement_session(self):
        joueur_table = []
        i = 1
        while self.ordre:
            for pseudo, rang in self.ordre.items():
                if self.ordre[pseudo] == i:
                    joueur_table.append(pseudo)
                    del self.ordre[pseudo]
                    break
            i += 1

        self.table = TableWindow(joueur_table)
        self.table.setWindowModality(Qt.ApplicationModal)
        self.close()
        self.table.show()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication


    app = QApplication()
    window = SelectJoueurWindow()
    window.show()
    app.exec()
