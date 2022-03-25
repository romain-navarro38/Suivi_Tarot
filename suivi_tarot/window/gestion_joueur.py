from functools import partial

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QCloseEvent
from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QListWidget, QPushButton, QListWidgetItem, \
    QAbstractItemView

from database.clients import get_joueur_actif, get_joueur_inactif, update_status_joueurs
from window.ajout_joueur import AjoutJoueurWindow
from api.utils import IMAGE_FOLDER


# noinspection PyAttributeOutsideInit
class GestionJoueurWindow(QWidget):
    """Fenêtre permettant l'ajout de nouveau joueur et leur passage de la
    catégorie actif à inactif et vice-versa"""
    def __init__(self, parent=None):
        super().__init__()

        self.parent = parent
        self.parent.setVisible(False)
        self.modif = {}
        self.new_joueur = False
        self.setup_ui()
        self.resize(318, 266)
        self.setWindowTitle("Gestion des joueurs")

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.lbl_inactif = QLabel("Inactif")
        self.lbl_actif = QLabel("Actif")
        self.lw_inactif = QListWidget()
        self.lw_actif = QListWidget()
        self.btn_transfert = QPushButton()
        self.btn_ajouter = QPushButton("Ajouter")
        self.btn_valider = QPushButton("Valider")
        self.btn_annuler = QPushButton("Annuler")

    def modify_widgets(self):
        self.lbl_inactif.setAlignment(Qt.AlignCenter)
        self.lbl_actif.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.lbl_actif.setFont(font)
        self.lbl_inactif.setFont(font)

        self.btn_transfert.setIcon(QIcon(str(IMAGE_FOLDER / "double_fleche_couleur.png")))
        self.btn_transfert.setIconSize(QSize(60, 40))
        self.btn_transfert.setFlat(True)

        # liste_joueur = [QListWidgetItem(j[0]).text() for j in get_joueur_inactif()]
        self.lw_inactif.addItems(get_joueur_inactif())
        self.lw_inactif.setSelectionMode(QAbstractItemView.MultiSelection)
        # liste_joueur = [QListWidgetItem(j[0]).text() for j in get_joueur_actif()]
        self.lw_actif.addItems(get_joueur_actif())
        self.lw_actif.setSelectionMode(QAbstractItemView.MultiSelection)

    def create_layouts(self):
        self.main_layout = QGridLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_inactif, 0, 0, 1, 2)
        self.main_layout.addWidget(self.lbl_actif, 0, 4, 1, 2)
        self.main_layout.addWidget(self.lw_inactif, 1, 0, 4, 2)
        self.main_layout.addWidget(self.lw_actif, 1, 4, 4, 2)
        self.main_layout.addWidget(self.btn_transfert, 2, 2, 2, 2)
        self.main_layout.addWidget(self.btn_ajouter, 0, 2, 1, 2)
        self.main_layout.addWidget(self.btn_valider, 5, 1, 1, 2)
        self.main_layout.addWidget(self.btn_annuler, 5, 3, 1, 2)

    def setup_connections(self):
        self.lw_inactif.itemDoubleClicked.connect(partial(self.transfert_unique, "inactif"))
        self.lw_actif.itemDoubleClicked.connect(partial(self.transfert_unique, "actif"))
        self.btn_ajouter.clicked.connect(self.ajouter_joueur)
        self.btn_transfert.clicked.connect(self.transfert_global)
        self.btn_valider.clicked.connect(self.save_changement)
        self.btn_annuler.clicked.connect(self.close)

    def ajouter_joueur(self):
        """Ouvre la fenêtre de création de nouveau joueur"""
        self.new_joueur = AjoutJoueurWindow()
        self.new_joueur.new_pseudo.connect(self.ajouter_pseudo_a_liste)
        self.new_joueur.etat_fenetre.connect(self.maj_etat_fenetre)
        self.new_joueur.show()

    def ajouter_pseudo_a_liste(self, joueur):
        """Ajoute un joueur à une des listes actif ou inactif après sa création."""
        if joueur["actif"]:
            self.lw_actif.addItem(joueur["pseudo"])
        else:
            self.lw_inactif.addItem(joueur["pseudo"])

    def maj_etat_fenetre(self, etat):
        """Renseigne l'état de la fenêtre de création de joueur permet de
        savoir s'il faut fermer cette dernière lorsque la fenêtre est fermée."""
        self.new_joueur = etat

    def closeEvent(self, event: QCloseEvent) -> None:
        """À la fermeture de la fenêtre, ferme également celle
        de création de joueur si elle est ouverte"""
        if self.new_joueur:
            self.new_joueur.close()
        self.parent.setVisible(True)
        super().closeEvent(event)

    def transfert_unique(self, lw: str, item: QListWidgetItem):
        """Bascule l'item double-cliqué d'une liste à l'autre"""
        if lw == "inactif":
            lw_depart = self.lw_inactif
            lw_arrive = self.lw_actif
            status = True
        else:
            lw_depart = self.lw_actif
            lw_arrive = self.lw_inactif
            status = False

        row = lw_depart.row(item)
        self.modif[item.text()] = status
        lw_arrive.addItem(lw_depart.takeItem(row))

    def transfert_global(self):
        """Bascule tous les items sélectionnés entre les deux listes"""
        for item in self.lw_inactif.selectedItems():
            row = self.lw_inactif.row(item)
            self.modif[item.text()] = True
            self.lw_actif.addItem(self.lw_inactif.takeItem(row))
        for item in self.lw_actif.selectedItems():
            row = self.lw_actif.row(item)
            self.modif[item.text()] = False
            self.lw_inactif.addItem(self.lw_actif.takeItem(row))

    def save_changement(self):
        """Sauvegarde en bdd l'attribut actif de chaque joueur"""
        if self.modif:
            update_status_joueurs(self.modif)
            self.close()


if __name__ == '__main__':
    app = QApplication()
    window = GestionJoueurWindow()
    window.show()
    app.exec()
