from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QAbstractItemView, \
    QListWidgetItem

from database.clients import get_joueur_actif
from window.table import TableWindow


# noinspection PyAttributeOutsideInit
class SelectJoueurWindow(QWidget):
    """Fenêtre de sélection des joueurs participants à la session"""
    def __init__(self):
        super().__init__()

        self.selected_players = set()
        self.selection_order = {}
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
        self.lw_joueur.itemSelectionChanged.connect(self.selection_joueur)
        self.btn_valider.clicked.connect(self.lancement_session)
        self.btn_annuler.clicked.connect(self.close)

    def selection_joueur(self):
        """Lance les actions après un changement de sélection dans le ListWidget"""
        self.order_of_selection()
        self.maj_interface()

    def maj_interface(self):
        """Active ou non le bouton valider en fonction du nombre de joueurs sélectionnés
        et affichage de ce dernier"""
        nb_select = len(self.selected_players)

        self.btn_valider.setEnabled(2 < nb_select < 7)
        self.lbl_nb_joueur.setText(f"{nb_select} sélectionné{'s' if nb_select > 1 else ''}")

    def order_of_selection(self):
        """Sauvegarde de l'ordre dans lequel les pseudos sont sélectionnés"""
        new_selected_players = {elem.text() for elem in self.lw_joueur.selectedItems()}
        if new_selected_players - self.selected_players:
            pseudo = (new_selected_players - self.selected_players).pop()
            self.selected_players.add(pseudo)
            self.selection_order[pseudo] = len(self.selected_players)
        else:
            pseudo = (self.selected_players - new_selected_players).pop()
            self.selected_players.remove(pseudo)
            rang = self.selection_order[pseudo]
            del self.selection_order[pseudo]
            for cle in self.selection_order:
                if self.selection_order[cle] > rang:
                    self.selection_order[cle] -= 1

    def lancement_session(self):
        """Ouvre la fenêtre d'enregistrement d'une session"""
        joueur_table = self.create_list_player_sorted()

        self.table = TableWindow(joueur_table)
        self.table.setWindowModality(Qt.ApplicationModal)
        self.close()
        self.table.show()

    def create_list_player_sorted(self):
        """Création de la liste des pseudos dans l'ordre où ils ont été sélectionnés"""
        list_sorted = []
        i = 1
        while self.selection_order:
            for pseudo, rang in self.selection_order.items():
                if self.selection_order[pseudo] == i:
                    list_sorted.append(pseudo)
                    del self.selection_order[pseudo]
                    break
            i += 1

        return list_sorted


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication


    app = QApplication()
    window = SelectJoueurWindow()
    window.show()
    app.exec()
